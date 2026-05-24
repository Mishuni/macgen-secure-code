package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
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
	Summary    string `json:"summary"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS entries (
		id TEXT PRIMARY KEY,
		title TEXT,
		content TEXT,
		lastModifiedBy TEXT,
		lastModifiedAt TEXT
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func main() {
	http.HandleFunc("/entries", entriesHandler)
	http.HandleFunc("/entries/", entryHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
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

func entryHandler(w http.ResponseWriter, r *http.Request) {
	entryID := r.URL.Path[len("/entries/"):]
	switch r.Method {
	case http.MethodGet:
		getEntry(w, entryID)
	case http.MethodPut:
		updateEntry(w, r, entryID)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func getEntries(w http.ResponseWriter) {
	rows, err := db.Query("SELECT id, title FROM entries")
	if err != nil {
		http.Error(w, "Failed to retrieve entries", http.StatusInternalServerError)
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

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(entries)
}

func createEntry(w http.ResponseWriter, r *http.Request) {
	var newEntry NewEntry
	if err := json.NewDecoder(r.Body).Decode(&newEntry); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	entryID := uuid.New().String()
	lastModifiedAt := time.Now().Format(time.RFC3339)
	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		entryID, newEntry.Title, newEntry.Content, newEntry.CreatedBy, lastModifiedAt)
	if err != nil {
		http.Error(w, "Failed to create entry", http.StatusInternalServerError)
		return
	}

	entry := Entry{
		ID:             entryID,
		Title:          newEntry.Title,
		Content:        newEntry.Content,
		LastModifiedBy: newEntry.CreatedBy,
		LastModifiedAt: lastModifiedAt,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(entry)
}

func getEntry(w http.ResponseWriter, entryID string) {
	var entry Entry
	err := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryID).Scan(
		&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Entry not found", http.StatusNotFound)
		} else {
			http.Error(w, "Failed to retrieve entry", http.StatusInternalServerError)
		}
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(entry)
}

func updateEntry(w http.ResponseWriter, r *http.Request, entryID string) {
	var updateEntry UpdateEntry
	if err := json.NewDecoder(r.Body).Decode(&updateEntry); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	lastModifiedAt := time.Now().Format(time.RFC3339)
	_, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, lastModifiedAt, entryID)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Entry not found", http.StatusNotFound)
		} else {
			http.Error(w, "Failed to update entry", http.StatusInternalServerError)
		}
		return
	}

	entry := Entry{
		ID:             entryID,
		Title:          updateEntry.Title,
		Content:        updateEntry.Content,
		LastModifiedBy: updateEntry.ModifiedBy,
		LastModifiedAt: lastModifiedAt,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(entry)
}