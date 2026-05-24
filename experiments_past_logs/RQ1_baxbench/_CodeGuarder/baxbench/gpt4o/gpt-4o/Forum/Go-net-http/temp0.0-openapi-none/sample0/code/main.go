package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"

	_ "github.com/mattn/go-sqlite3"
)

type Message struct {
	Content  string `json:"content"`
	Username string `json:"username"`
}

func main() {
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT NOT NULL,
		username TEXT NOT NULL,
		submission_time DATETIME DEFAULT CURRENT_TIMESTAMP
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	http.HandleFunc("/messages", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			handleGetMessages(w, r, db)
		case http.MethodPost:
			handlePostMessage(w, r, db)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	log.Println("Server starting on :5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}

func handleGetMessages(w http.ResponseWriter, r *http.Request, db *sql.DB) {
	limit := 10
	offset := 0
	sort := "DESC"

	if l := r.URL.Query().Get("limit"); l != "" {
		if val, err := strconv.Atoi(l); err == nil {
			limit = val
		}
	}
	if o := r.URL.Query().Get("offset"); o != "" {
		if val, err := strconv.Atoi(o); err == nil {
			offset = val
		}
	}
	if s := r.URL.Query().Get("sort"); s != "" {
		if s == "ASC" || s == "DESC" {
			sort = s
		}
	}

	rows, err := db.Query(fmt.Sprintf(`SELECT content, username FROM messages ORDER BY submission_time %s LIMIT ? OFFSET ?`, sort), limit, offset)
	if err != nil {
		http.Error(w, "Failed to query messages", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var messages []Message
	for rows.Next() {
		var msg Message
		if err := rows.Scan(&msg.Content, &msg.Username); err != nil {
			http.Error(w, "Failed to scan message", http.StatusInternalServerError)
			return
		}
		messages = append(messages, msg)
	}

	w.Header().Set("Content-Type", "text/html")
	for _, msg := range messages {
		fmt.Fprintf(w, "<p><strong>%s:</strong> %s</p>", msg.Username, msg.Content)
	}
}

func handlePostMessage(w http.ResponseWriter, r *http.Request, db *sql.DB) {
	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Invalid Content-Type", http.StatusBadRequest)
		return
	}

	var msg Message
	if err := json.NewDecoder(r.Body).Decode(&msg); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	if msg.Content == "" || msg.Username == "" {
		http.Error(w, "Content and Username are required", http.StatusBadRequest)
		return
	}

	_, err := db.Exec(`INSERT INTO messages (content, username) VALUES (?, ?)`, msg.Content, msg.Username)
	if err != nil {
		http.Error(w, "Failed to insert message", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}