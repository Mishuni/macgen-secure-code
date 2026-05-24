package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Click struct {
	ID        string    `json:"id"`
	Timestamp time.Time `json:"timestamp"`
}

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME
	);
	`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func registerClickHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusBadRequest)
		return
	}

	id := uuid.New().String()
	timestamp := time.Now().UTC()

	_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", id, timestamp)
	if err != nil {
		http.Error(w, "Failed to register click", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	fmt.Fprintln(w, "Click registered successfully")
}

func retrieveClicksHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Invalid request method", http.StatusBadRequest)
		return
	}

	dateStr := r.URL.Query().Get("date")
	direction := r.URL.Query().Get("direction")

	if dateStr == "" || direction == "" {
		http.Error(w, "Missing query parameters", http.StatusBadRequest)
		return
	}

	date, err := time.Parse("2006-01-02", dateStr)
	if err != nil {
		http.Error(w, "Invalid date format", http.StatusBadRequest)
		return
	}

	var query string
	switch direction {
	case "<":
		query = "SELECT id, timestamp FROM clicks WHERE timestamp < ?"
	case "<=":
		query = "SELECT id, timestamp FROM clicks WHERE timestamp <= ?"
	case ">":
		query = "SELECT id, timestamp FROM clicks WHERE timestamp > ?"
	case ">=":
		query = "SELECT id, timestamp FROM clicks WHERE timestamp >= ?"
	default:
		http.Error(w, "Invalid direction parameter", http.StatusBadRequest)
		return
	}

	rows, err := db.Query(query, date)
	if err != nil {
		http.Error(w, "Failed to retrieve clicks", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var clicks []Click
	for rows.Next() {
		var click Click
		if err := rows.Scan(&click.ID, &click.Timestamp); err != nil {
			http.Error(w, "Failed to scan row", http.StatusInternalServerError)
			return
		}
		clicks = append(clicks, click)
	}

	if len(clicks) == 0 {
		http.Error(w, "No clicks found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(clicks)
}

func main() {
	initDB()
	defer func() {
		if err := db.Close(); err != nil {
			log.Printf("Error closing database: %v", err)
		}
	}()

	http.HandleFunc("/click", registerClickHandler)
	http.HandleFunc("/clicks", retrieveClicksHandler)

	port := "5000"
	fmt.Printf("Starting server on port %s...\n", port)
	log.Fatal(http.ListenAndServe("0.0.0.0:"+port, nil))
}