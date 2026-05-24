package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
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

func main() {
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME NOT NULL
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	http.HandleFunc("/click", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		id := uuid.New().String()
		timestamp := time.Now()

		_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", id, timestamp)
		if err != nil {
			log.Printf("Failed to insert click: %v", err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusCreated)
		fmt.Fprintln(w, "Click registered successfully")
	})

	http.HandleFunc("/clicks", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		date := r.URL.Query().Get("date")
		direction := r.URL.Query().Get("direction")

		if date == "" || direction == "" {
			http.Error(w, "Missing query parameters", http.StatusBadRequest)
			return
		}

		if direction != ">" && direction != "<" {
			http.Error(w, "Invalid direction parameter", http.StatusBadRequest)
			return
		}

		parsedDate, err := time.Parse("2006-01-02", date)
		if err != nil {
			http.Error(w, "Invalid date format", http.StatusBadRequest)
			return
		}

		query := "SELECT id, timestamp FROM clicks WHERE timestamp " + direction + " ?"
		rows, err := db.Query(query, parsedDate)
		if err != nil {
			log.Printf("Failed to query clicks: %v", err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}
		defer rows.Close()

		var clicks []Click
		for rows.Next() {
			var click Click
			var timestamp string
			if err := rows.Scan(&click.ID, &timestamp); err != nil {
				log.Printf("Failed to scan row: %v", err)
				http.Error(w, "Internal server error", http.StatusInternalServerError)
				return
			}
			click.Timestamp, err = time.Parse("2006-01-02 15:04:05", timestamp)
			if err != nil {
				log.Printf("Failed to parse timestamp: %v", err)
				http.Error(w, "Internal server error", http.StatusInternalServerError)
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
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "5000"
	}

	log.Printf("Server starting on port %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}