package main

import (
	"encoding/json"
	"net/http"
	"os"
	"strconv"

	"database/sql"
	"github.com/mattn/go-sqlite3"
)

type Message struct {
	Content  string `json:"content"`
	Username string `json:"username"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create messages table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT,
		username TEXT,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	)`)
	if err != nil {
		panic(err)
	}

	http.HandleFunc("/messages", messagesHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func messagesHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		getMessages(w, r)
	case http.MethodPost:
		postMessage(w, r)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func getMessages(w http.ResponseWriter, r *http.Request) {
	limit := 10
	offset := 0
	sort := "DESC"

	if r.URL.Query().Get("limit") != "" {
		if l, err := strconv.Atoi(r.URL.Query().Get("limit")); err == nil {
			limit = l
		}
	}
	if r.URL.Query().Get("offset") != "" {
		if o, err := strconv.Atoi(r.URL.Query().Get("offset")); err == nil {
			offset = o
		}
	}
	if r.URL.Query().Get("sort") != "" {
		sort = r.URL.Query().Get("sort")
		if sort != "ASC" && sort != "DESC" {
			http.Error(w, "Invalid sort parameter", http.StatusBadRequest)
			return
		}
	}

	rows, err := db.Query("SELECT content, username FROM messages ORDER BY created_at " + sort + " LIMIT ? OFFSET ?", limit, offset)
	if err != nil {
		http.Error(w, "Failed to retrieve messages", http.StatusInternalServerError)
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

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(messages)
}

func postMessage(w http.ResponseWriter, r *http.Request) {
	var msg Message
	if err := json.NewDecoder(r.Body).Decode(&msg); err != nil || msg.Content == "" || msg.Username == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO messages (content, username) VALUES (?, ?)", msg.Content, msg.Username)
	if err != nil {
		http.Error(w, "Failed to post message", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}