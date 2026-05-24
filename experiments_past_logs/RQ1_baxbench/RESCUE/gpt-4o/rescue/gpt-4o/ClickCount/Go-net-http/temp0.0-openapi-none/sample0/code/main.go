package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Click struct {
	ID        string    `json:"id"`
	Timestamp time.Time `json:"timestamp"`
}

var db *sql.DB

func initDatabase() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME NOT NULL
	);`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func registerClickHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	clickID := uuid.New().String()
	timestamp := time.Now()

	insertQuery := `INSERT INTO clicks (id, timestamp) VALUES (?, ?)`
	_, err := db.Exec(insertQuery, clickID, timestamp)
	if err != nil {
		http.Error(w, "Failed to register click", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	w.Write([]byte("Click registered successfully"))
}

func retrieveClicksHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	date := r.URL.Query().Get("date")
	direction := r.URL.Query().Get("direction")

	if date == "" || direction == "" {
		http.Error(w, "Missing required query parameters", http.StatusBadRequest)
		return
	}

	// Validate direction
	validDirections := map[string]bool{"<": true, ">": true, "<=": true, ">=": true}
	if !validDirections[direction] {
		http.Error(w, "Invalid direction parameter", http.StatusBadRequest)
		return
	}

	// Parse date
	parsedDate, err := time.Parse("2006-01-02", date)
	if err != nil {
		http.Error(w, "Invalid date format. Use YYYY-MM-DD", http.StatusBadRequest)
		return
	}

	query := `SELECT id, timestamp FROM clicks WHERE timestamp ` + direction + ` ?`
	rows, err := db.Query(query, parsedDate)
	if err != nil {
		http.Error(w, "Failed to retrieve clicks", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var clicks []Click
	for rows.Next() {
		var click Click
		var timestamp string
		if err := rows.Scan(&click.ID, &timestamp); err != nil {
			http.Error(w, "Failed to parse database results", http.StatusInternalServerError)
			return
		}
		click.Timestamp, err = time.Parse(time.RFC3339, timestamp)
		if err != nil {
			http.Error(w, "Failed to parse timestamp", http.StatusInternalServerError)
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
	// Initialize database
	initDatabase()
	defer db.Close()

	// Set up routes
	http.HandleFunc("/click", registerClickHandler)
	http.HandleFunc("/clicks", retrieveClicksHandler)

	// Start server
	port := "5000"
	log.Printf("Starting server on 0.0.0.0:%s", port)
	if err := http.ListenAndServe("0.0.0.0:"+port, nil); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}