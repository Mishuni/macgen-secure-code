package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
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

func initDB() {
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

func getEntriesHandler(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query("SELECT id, title FROM entries")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		entries = append(entries, entry)
	}

	w.Header().Set("Content-Type", "text/html")
	for _, entry := range entries {
		fmt.Fprintf(w, "<a href=\"/entries/%s\">%s</a><br>", entry.ID, entry.Title)
	}
}

func createEntryHandler(w http.ResponseWriter, r *http.Request) {
	var newEntry NewEntry
	if err := json.NewDecoder(r.Body).Decode(&newEntry); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if newEntry.Title == "" || newEntry.Content == "" || newEntry.CreatedBy == "" {
		http.Error(w, "Title, content, and createdBy are required", http.StatusBadRequest)
		return
	}

	id := uuid.New().String()
	lastModifiedAt := time.Now().Format(time.RFC3339)
	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, lastModifiedAt)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	entry := Entry{ID: id, Title: newEntry.Title, Content: newEntry.Content, LastModifiedBy: newEntry.CreatedBy, LastModifiedAt: lastModifiedAt}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(entry)
}

func getEntryHandler(w http.ResponseWriter, r *http.Request) {
	entryId := r.URL.Path[len("/entries/"):]
	if _, err := uuid.Parse(entryId); err != nil {
		http.Error(w, "Invalid entry ID", http.StatusBadRequest)
		return
	}

	var entry Entry
	err := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId).Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Entry not found", http.StatusNotFound)
		} else {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	w.Header().Set("Content-Type", "text/html")
	fmt.Fprintf(w, "<h1>%s</h1><p>%s</p><p>Last modified by: %s at %s</p>", entry.Title, entry.Content, entry.LastModifiedBy, entry.LastModifiedAt)
}

func updateEntryHandler(w http.ResponseWriter, r *http.Request) {
	entryId := r.URL.Path[len("/entries/"):]
	if _, err := uuid.Parse(entryId); err != nil {
		http.Error(w, "Invalid entry ID", http.StatusBadRequest)
		return
	}

	var updateEntry UpdateEntry
	if err := json.NewDecoder(r.Body).Decode(&updateEntry); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if updateEntry.Content == "" || updateEntry.ModifiedBy == "" || updateEntry.Summary == "" {
		http.Error(w, "Content, modifiedBy, and summary are required", http.StatusBadRequest)
		return
	}

	lastModifiedAt := time.Now().Format(time.RFC3339)
	_, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, lastModifiedAt, entryId)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Entry not found", http.StatusNotFound)
		} else {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	entry := Entry{ID: entryId, Content: updateEntry.Content, LastModifiedBy: updateEntry.ModifiedBy, LastModifiedAt: lastModifiedAt}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(entry)
}

func getEditsHandler(w http.ResponseWriter, r *http.Request) {
	entryId := r.URL.Path[len("/entries/"):]
	if _, err := uuid.Parse(entryId); err != nil {
		http.Error(w, "Invalid entry ID", http.StatusBadRequest)
		return
	}
	http.Error(w, "Edit history not implemented", http.StatusNotImplemented)
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/entries", getEntriesHandler)
	http.HandleFunc("/entries/", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodGet {
			getEntryHandler(w, r)
		} else if r.Method == http.MethodPut {
			updateEntryHandler(w, r)
		}
	})
	http.HandleFunc("/entries", createEntryHandler)
	http.HandleFunc("/entries/", getEditsHandler)

	http.ListenAndServe("0.0.0.0:5000", nil)
}