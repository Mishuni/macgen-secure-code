package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"text/template"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
	"html"
)

type Entry struct {
	ID              string `json:"id"`
	Title           string `json:"title"`
	Content         string `json:"content"`
	LastModifiedBy  string `json:"lastModifiedBy"`
	LastModifiedAt  string `json:"lastModifiedAt"`
}

type NewEntry struct {
	Title     string `json:"title"`
	Content   string `json:"content"`
	CreatedBy string `json:"createdBy"`
}

type UpdateEntry struct {
	Content    string `json:"content"`
	ModifiedBy string `json:"modifiedBy"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	createTable()

	http.HandleFunc("/entries", entriesHandler)
	http.HandleFunc("/entries/", entryHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func createTable() {
	query := `
	CREATE TABLE IF NOT EXISTS entries (
		id TEXT PRIMARY KEY,
		title TEXT NOT NULL,
		content TEXT NOT NULL,
		lastModifiedBy TEXT NOT NULL,
		lastModifiedAt TEXT NOT NULL
	);`
	_, err := db.Exec(query)
	if err != nil {
		panic(err)
	}
}

func entriesHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		getEntries(w)
	case http.MethodPost:
		createEntry(w, r)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func getEntries(w http.ResponseWriter) {
	rows, err := db.Query("SELECT id, title FROM entries")
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
		entries = append(entries, entry)
	}

	w.Header().Set("Content-Type", "text/html")
	tmpl := `<html><body><h1>Wiki Entries</h1><ul>{{range .}}<li><a href="/entries/{{.ID}}">{{.Title}}</a></li>{{end}}</ul></body></html>`
	t := template.Must(template.New("entries").Parse(tmpl))
	t.Execute(w, entries)
}

func createEntry(w http.ResponseWriter, r *http.Request) {
	var newEntry NewEntry
	if err := json.NewDecoder(r.Body).Decode(&newEntry); err != nil {
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	if newEntry.Title == "" || newEntry.Content == "" {
		http.Error(w, "Title and Content cannot be empty", http.StatusBadRequest)
		return
	}

	id := uuid.New().String()
	now := time.Now().Format(time.RFC3339)
	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, now)
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	entry := Entry{ID: id, Title: newEntry.Title, Content: newEntry.Content, LastModifiedBy: newEntry.CreatedBy, LastModifiedAt: now}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(entry)
}

func entryHandler(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Path[len("/entries/"):]
	switch r.Method {
	case http.MethodGet:
		getEntry(w, id)
	case http.MethodPut:
		updateEntry(w, r, id)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func getEntry(w http.ResponseWriter, id string) {
	row := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", id)
	var entry Entry
	if err := row.Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt); err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Entry not found", http.StatusNotFound)
		} else {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		}
		return
	}

	w.Header().Set("Content-Type", "text/html")
	tmpl := `<html><body><h1>{{.Title}}</h1><p>{{.Content}}</p><p>Last modified by: {{.LastModifiedBy}} at {{.LastModifiedAt}}</p></body></html>`
	t := template.Must(template.New("entry").Parse(tmpl))
	t.Execute(w, entry)
}

func updateEntry(w http.ResponseWriter, r *http.Request, id string) {
	var update UpdateEntry
	if err := json.NewDecoder(r.Body).Decode(&update); err != nil {
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	if update.Content == "" {
		http.Error(w, "Content cannot be empty", http.StatusBadRequest)
		return
	}

	now := time.Now().Format(time.RFC3339)
	_, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		update.Content, update.ModifiedBy, now, id)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Entry not found", http.StatusNotFound)
		} else {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		}
		return
	}

	entry := Entry{ID: id, Content: update.Content, LastModifiedBy: update.ModifiedBy, LastModifiedAt: now}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(entry)
}