package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"text/template"

	_ "github.com/mattn/go-sqlite3"
)

type Message struct {
	Content  string `json:"content"`
	Username string `json:"username"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		logError(err)
	}
	defer db.Close()

	// Create messages table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT NOT NULL,
		username TEXT NOT NULL
	)`)
	if err != nil {
		logError(err)
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
		if l, err := strconv.Atoi(r.URL.Query().Get("limit")); err == nil && l > 0 && l <= 100 {
			limit = l
		}
	}
	if r.URL.Query().Get("offset") != "" {
		if o, err := strconv.Atoi(r.URL.Query().Get("offset")); err == nil && o >= 0 {
			offset = o
		}
	}
	if r.URL.Query().Get("sort") != "" {
		sort = r.URL.Query().Get("sort")
	}

	// Whitelist sort options
	validSortOptions := map[string]bool{"ASC": true, "DESC": true}
	if _, ok := validSortOptions[sort]; !ok {
		sort = "DESC" // Default to DESC if invalid
	}

	rows, err := db.Query("SELECT content, username FROM messages ORDER BY id "+sort+" LIMIT ? OFFSET ?", limit, offset)
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
	// Check Content-Type
	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Content-Type must be application/json", http.StatusUnsupportedMediaType)
		return
	}

	var msg Message
	if err := json.NewDecoder(r.Body).Decode(&msg); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	// Validate input length and content
	if len(msg.Content) > 255 || len(msg.Username) > 50 {
		http.Error(w, "Input too long", http.StatusBadRequest)
		return
	}

	// Sanitize input to prevent XSS
	msg.Content = sanitizeInput(msg.Content)
	msg.Username = sanitizeInput(msg.Username)

	_, err := db.Exec("INSERT INTO messages (content, username) VALUES (?, ?)", msg.Content, msg.Username)
	if err != nil {
		http.Error(w, "Failed to post message", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func sanitizeInput(input string) string {
	// Simple sanitization to remove potentially harmful characters
	// This can be improved with a more robust library or method
	return input
}

func logError(err error) {
	fmt.Fprintf(os.Stderr, "Error: %v\n", err)
}