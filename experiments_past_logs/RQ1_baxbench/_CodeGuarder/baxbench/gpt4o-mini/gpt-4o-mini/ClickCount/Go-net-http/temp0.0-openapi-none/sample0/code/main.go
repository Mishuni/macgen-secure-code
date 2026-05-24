package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Click struct {
	ID        string    `json:"id"`
	Timestamp time.Time `json:"timestamp"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func registerClick(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	click := Click{
		ID:        uuid.NewString(),
		Timestamp: time.Now(),
	}

	_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", click.ID, click.Timestamp)
	if err != nil {
		http.Error(w, "Failed to register click", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(click)
}

func retrieveClicks(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	date := r.URL.Query().Get("date")
	direction := r.URL.Query().Get("direction")

	if date == "" || direction == "" {
		http.Error(w, "Missing query parameters", http.StatusBadRequest)
		return
	}

	var operator string
	switch direction {
	case "<":
		operator = "<"
	case "<=":
		operator = "<="
	case ">":
		operator = ">"
	case ">=":
		operator = ">="
	default:
		http.Error(w, "Invalid direction parameter", http.StatusBadRequest)
		return
	}

	query := fmt.Sprintf("SELECT id, timestamp FROM clicks WHERE timestamp %s ?", operator)
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
			http.Error(w, "Failed to scan click", http.StatusInternalServerError)
			return
		}
		clicks = append(clicks, click)
	}

	if len(clicks) == 0 {
		http.Error(w, "No clicks found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(clicks)
}

func main() {
	http.HandleFunc("/click", registerClick)
	http.HandleFunc("/clicks", retrieveClicks)

	log.Println("Server starting on :5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatal(err)
	}
}