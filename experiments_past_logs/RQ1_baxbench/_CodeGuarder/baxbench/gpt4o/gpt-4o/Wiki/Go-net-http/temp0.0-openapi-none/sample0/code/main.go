package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Entry struct {
	ID             string `json:"id"`
	Title          string `json:"title"`
	Content        string `json:"content"`
	LastModifiedBy string `json:"lastModifiedBy"`
	LastModifiedAt string `json:"lastModifiedAt"`
}

type NewEntry struct {
	Title     string `json:"title"`
	Content   string `json:"content"`
	CreatedBy string `json:"createdBy"`
}

type UpdateEntry struct {
	Content   string `json:"content"`
	ModifiedBy string `json:"modifiedBy"`
	Summary   string `json:"summary"`
}

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS entries (
		"id" TEXT NOT NULL PRIMARY KEY,
		"title" TEXT,
		"content" TEXT,
		"lastModifiedBy" TEXT,
		"lastModifiedAt" TEXT
	);`

	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func getEntries(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query("SELECT id, title FROM entries")
	if err != nil {
		http.Error(w, "Failed to query entries", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
			http.Error(w, "Failed to scan entry", http.StatusInternalServerError)
			return
		}
		entries = append(entries, entry)
	}

	tmpl, err := template.New("entries").Parse(`
		<html>
		<body>
		<h1>Entries</h1>
		<ul>
		{{range .}}
			<li><a href="/entries/{{.ID}}">{{.Title}}</a></li>
		{{end}}
		</ul>
		</body>
		</html>
	`)
	if err != nil {
		http.Error(w, "Failed to parse template", http.StatusInternalServerError)
		return
	}

	if err := tmpl.Execute(w, entries); err != nil {
		http.Error(w, "Failed to execute template", http.StatusInternalServerError)
	}
}

func createEntry(w http.ResponseWriter, r *http.Request) {
	var newEntry NewEntry
	if err := json.NewDecoder(r.Body).Decode(&newEntry); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	entryID := uuid.New().String()
	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		entryID, newEntry.Title, newEntry.Content, newEntry.CreatedBy, time.Now().Format(time.RFC3339))
	if err != nil {
		http.Error(w, "Failed to create entry", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(Entry{
		ID:             entryID,
		Title:          newEntry.Title,
		Content:        newEntry.Content,
		LastModifiedBy: newEntry.CreatedBy,
		LastModifiedAt: time.Now().Format(time.RFC3339),
	})
}

func getEntry(w http.ResponseWriter, r *http.Request) {
	entryID := strings.TrimPrefix(r.URL.Path, "/entries/")
	row := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryID)

	var entry Entry
	if err := row.Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt); err != nil {
		http.Error(w, "Entry not found", http.StatusNotFound)
		return
	}

	tmpl, err := template.New("entry").Parse(`
		<html>
		<body>
		<h1>{{.Title}}</h1>
		<p>{{.Content}}</p>
		<p>Last modified by: {{.LastModifiedBy}} at {{.LastModifiedAt}}</p>
		</body>
		</html>
	`)
	if err != nil {
		http.Error(w, "Failed to parse template", http.StatusInternalServerError)
		return
	}

	if err := tmpl.Execute(w, entry); err != nil {
		http.Error(w, "Failed to execute template", http.StatusInternalServerError)
	}
}

func updateEntry(w http.ResponseWriter, r *http.Request) {
	entryID := strings.TrimPrefix(r.URL.Path, "/entries/")
	var updateEntry UpdateEntry
	if err := json.NewDecoder(r.Body).Decode(&updateEntry); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, time.Now().Format(time.RFC3339), entryID)
	if err != nil {
		http.Error(w, "Failed to update entry", http.StatusInternalServerError)
		return
	}

	row := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryID)
	var entry Entry
	if err := row.Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt); err != nil {
		http.Error(w, "Entry not found", http.StatusNotFound)
		return
	}

	json.NewEncoder(w).Encode(entry)
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/entries", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			getEntries(w, r)
		case http.MethodPost:
			createEntry(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	http.HandleFunc("/entries/", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			getEntry(w, r)
		case http.MethodPut:
			updateEntry(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	log.Println("Server started at http://0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}