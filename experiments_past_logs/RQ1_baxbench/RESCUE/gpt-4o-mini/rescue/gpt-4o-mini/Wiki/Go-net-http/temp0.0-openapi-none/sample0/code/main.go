package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"github.com/google/uuid"
	"database/sql"
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
	Content    string `json:"content"`
	ModifiedBy string `json:"modifiedBy"`
	Summary    string `json:"summary"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		fmt.Println("Error opening database:", err)
		return
	}
	defer db.Close()

	createTable()

	http.HandleFunc("/entries", entriesHandler)
	http.HandleFunc("/entries/", entryHandler)

	fmt.Println("Server is running on http://0.0.0.0:5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func createTable() {
	createEntriesTableSQL := `CREATE TABLE IF NOT EXISTS entries (
		id TEXT PRIMARY KEY,
		title TEXT,
		content TEXT,
		lastModifiedBy TEXT,
		lastModifiedAt TEXT
	);`
	_, err := db.Exec(createEntriesTableSQL)
	if err != nil {
		fmt.Println("Error creating table:", err)
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
		http.Error(w, "Error fetching entries", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
			http.Error(w, "Error scanning entry", http.StatusInternalServerError)
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

	id := uuid.New().String()
	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, "now")
	if err != nil {
		http.Error(w, "Error creating entry", http.StatusInternalServerError)
		return
	}

	entry := Entry{ID: id, Title: newEntry.Title, Content: newEntry.Content, LastModifiedBy: newEntry.CreatedBy, LastModifiedAt: "now"}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(entry)
}

func entryHandler(w http.ResponseWriter, r *http.Request) {
	entryId := r.URL.Path[len("/entries/"):]

	switch r.Method {
	case http.MethodGet:
		getEntry(w, entryId)
	case http.MethodPut:
		updateEntry(w, r, entryId)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func getEntry(w http.ResponseWriter, entryId string) {
	row := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId)

	var entry Entry
	if err := row.Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt); err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Entry not found", http.StatusNotFound)
		} else {
			http.Error(w, "Error fetching entry", http.StatusInternalServerError)
		}
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(entry)
}

func updateEntry(w http.ResponseWriter, r *http.Request, entryId string) {
	var updateEntry UpdateEntry
	if err := json.NewDecoder(r.Body).Decode(&updateEntry); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, "now", entryId)
	if err != nil {
		http.Error(w, "Error updating entry", http.StatusInternalServerError)
		return
	}

	entry := Entry{ID: entryId, Content: updateEntry.Content, LastModifiedBy: updateEntry.ModifiedBy, LastModifiedAt: "now"}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(entry)
}