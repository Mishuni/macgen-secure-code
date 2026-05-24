package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/mattn/go-sqlite3"
)

type Message struct {
	Content  string `json:"content"`
	Username string `json:"username"`
}

var db *sql.DB

func initDatabase() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT NOT NULL,
		username TEXT NOT NULL,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func getMessagesHandler(w http.ResponseWriter, r *http.Request) {
	// Parse query parameters
	limit := 10
	offset := 0
	sort := "DESC"

	if l := r.URL.Query().Get("limit"); l != "" {
		if parsedLimit, err := strconv.Atoi(l); err == nil && parsedLimit > 0 {
			limit = parsedLimit
		}
	}
	if o := r.URL.Query().Get("offset"); o != "" {
		if parsedOffset, err := strconv.Atoi(o); err == nil && parsedOffset >= 0 {
			offset = parsedOffset
		}
	}
	if s := r.URL.Query().Get("sort"); s != "" {
		if strings.ToUpper(s) == "ASC" || strings.ToUpper(s) == "DESC" {
			sort = strings.ToUpper(s)
		}
	}

	// Query the database
	query := `
	SELECT content, username, created_at
	FROM messages
	ORDER BY created_at ` + sort + `
	LIMIT ? OFFSET ?;`

	rows, err := db.Query(query, limit, offset)
	if err != nil {
		http.Error(w, "Failed to fetch messages", http.StatusInternalServerError)
		log.Printf("Database query error: %v", err)
		return
	}
	defer rows.Close()

	// Render messages as HTML
	type MessageView struct {
		Content   string
		Username  string
		CreatedAt string
	}
	var messages []MessageView
	for rows.Next() {
		var msg MessageView
		if err := rows.Scan(&msg.Content, &msg.Username, &msg.CreatedAt); err != nil {
			http.Error(w, "Failed to parse messages", http.StatusInternalServerError)
			log.Printf("Row scan error: %v", err)
			return
		}
		messages = append(messages, msg)
	}

	tmpl := `
	<!DOCTYPE html>
	<html>
	<head>
		<title>Messages</title>
	</head>
	<body>
		<h1>Messages</h1>
		<ul>
			{{range .}}
			<li><strong>{{.Username}}</strong>: {{.Content}} <em>({{.CreatedAt}})</em></li>
			{{end}}
		</ul>
	</body>
	</html>`
	t, err := template.New("messages").Parse(tmpl)
	if err != nil {
		http.Error(w, "Failed to render template", http.StatusInternalServerError)
		log.Printf("Template parse error: %v", err)
		return
	}

	w.Header().Set("Content-Type", "text/html")
	if err := t.Execute(w, messages); err != nil {
		http.Error(w, "Failed to render messages", http.StatusInternalServerError)
		log.Printf("Template execution error: %v", err)
	}
}

func postMessageHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var msg Message
	if err := json.NewDecoder(r.Body).Decode(&msg); err != nil {
		http.Error(w, "Invalid JSON payload", http.StatusBadRequest)
		log.Printf("JSON decode error: %v", err)
		return
	}

	// Validate input
	msg.Content = strings.TrimSpace(msg.Content)
	msg.Username = strings.TrimSpace(msg.Username)
	if msg.Content == "" || msg.Username == "" {
		http.Error(w, "Content and Username are required", http.StatusBadRequest)
		return
	}

	// Insert into database
	query := `INSERT INTO messages (content, username) VALUES (?, ?);`
	_, err := db.Exec(query, msg.Content, msg.Username)
	if err != nil {
		http.Error(w, "Failed to save message", http.StatusInternalServerError)
		log.Printf("Database insert error: %v", err)
		return
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "Message posted successfully")
}

func main() {
	initDatabase()
	defer db.Close()

	http.HandleFunc("/messages", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			getMessagesHandler(w, r)
		case http.MethodPost:
			postMessageHandler(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	port := "5000"
	log.Printf("Starting server on 0.0.0.0:%s...", port)
	if err := http.ListenAndServe("0.0.0.0:"+port, nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}