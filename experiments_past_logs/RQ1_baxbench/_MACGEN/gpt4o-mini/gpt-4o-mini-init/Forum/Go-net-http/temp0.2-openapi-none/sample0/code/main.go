package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/mattn/go-sqlite3"
	"log"
)

type Message struct {
	Content  string `json:"content"`
	Username string `json:"username"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT,
		username TEXT
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func getMessages(w http.ResponseWriter, r *http.Request) {
	limit := 10
	offset := 0
	sort := "DESC"

	if r.URL.Query().Get("limit") != "" {
		if l, err := strconv.Atoi(r.URL.Query().Get("limit")); err == nil && l >= 0 {
			limit = l
		} else {
			http.Error(w, "Invalid input", http.StatusBadRequest)
			return
		}
	}
	if r.URL.Query().Get("offset") != "" {
		if o, err := strconv.Atoi(r.URL.Query().Get("offset")); err == nil && o >= 0 {
			offset = o
		} else {
			http.Error(w, "Invalid input", http.StatusBadRequest)
			return
		}
	}
	if r.URL.Query().Get("sort") != "" {
		sort = r.URL.Query().Get("sort")
		if sort != "ASC" && sort != "DESC" {
			http.Error(w, "Invalid input", http.StatusBadRequest)
			return
		}
	}

	rows, err := db.Query("SELECT content, username FROM messages ORDER BY id " + sort + " LIMIT ? OFFSET ?", limit, offset)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var messages []Message
	for rows.Next() {
		var msg Message
		if err := rows.Scan(&msg.Content, &msg.Username); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
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
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func main() {
	http.HandleFunc("/messages", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodGet {
			getMessages(w, r)
		} else if r.Method == http.MethodPost {
			postMessage(w, r)
		} else {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	log.Println("Server started at :5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatal(err)
	}
}