package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
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
	Content    string `json:"content"`
	ModifiedBy string `json:"modifiedBy"`
	Summary    string `json:"summary"`
}

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTable := `
	CREATE TABLE IF NOT EXISTS entries (
		id TEXT PRIMARY KEY,
		title TEXT,
		content TEXT,
		lastModifiedBy TEXT,
		lastModifiedAt TEXT
	);
	CREATE TABLE IF NOT EXISTS edits (
		id TEXT PRIMARY KEY,
		entryId TEXT,
		modifiedBy TEXT,
		summary TEXT,
		modifiedAt TEXT,
		FOREIGN KEY(entryId) REFERENCES entries(id)
	);
	`
	_, err = db.Exec(createTable)
	if err != nil {
		log.Fatal(err)
	}
}

func getEntries(w http.ResponseWriter, r *http.Request) {
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

	tmpl := `<html><body><h1>Entries</h1><ul>{{range .}}<li><a href="/entries/{{.ID}}">{{.Title}}</a></li>{{end}}</ul></body></html>`
	t, err := template.New("entries").Parse(tmpl)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	t.Execute(w, entries)
}

func createEntry(w http.ResponseWriter, r *http.Request) {
	var newEntry NewEntry
	if err := json.NewDecoder(r.Body).Decode(&newEntry); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	id := uuid.New().String()
	now := time.Now().Format(time.RFC3339)
	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, now)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	entry := Entry{
		ID:             id,
		Title:          newEntry.Title,
		Content:        newEntry.Content,
		LastModifiedBy: newEntry.CreatedBy,
		LastModifiedAt: now,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(entry)
}

func getEntry(w http.ResponseWriter, r *http.Request) {
	entryId := strings.TrimPrefix(r.URL.Path, "/entries/")
	entryId = strings.Split(entryId, "/")[0]

	var entry Entry
	err := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId).
		Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)
	if err == sql.ErrNoRows {
		http.Error(w, "Entry not found", http.StatusNotFound)
		return
	} else if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	tmpl := `<html><body><h1>{{.Title}}</h1><p>{{.Content}}</p><p>Last modified by: {{.LastModifiedBy}} at {{.LastModifiedAt}}</p></body></html>`
	t, err := template.New("entry").Parse(tmpl)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	t.Execute(w, entry)
}

func updateEntry(w http.ResponseWriter, r *http.Request) {
	entryId := strings.TrimPrefix(r.URL.Path, "/entries/")
	entryId = strings.Split(entryId, "/")[0]

	var updateEntry UpdateEntry
	if err := json.NewDecoder(r.Body).Decode(&updateEntry); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	now := time.Now().Format(time.RFC3339)
	_, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, now, entryId)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("INSERT INTO edits (id, entryId, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?)",
		uuid.New().String(), entryId, updateEntry.ModifiedBy, updateEntry.Summary, now)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	var entry Entry
	err = db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId).
		Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(entry)
}

func getEntryEdits(w http.ResponseWriter, r *http.Request) {
	entryId := strings.TrimPrefix(r.URL.Path, "/entries/")
	entryId = strings.TrimSuffix(entryId, "/edits")

	rows, err := db.Query("SELECT modifiedBy, summary, modifiedAt FROM edits WHERE entryId = ?", entryId)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	type Edit struct {
		ModifiedBy string
		Summary    string
		ModifiedAt string
	}

	var edits []Edit
	for rows.Next() {
		var edit Edit
		if err := rows.Scan(&edit.ModifiedBy, &edit.Summary, &edit.ModifiedAt); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		edits = append(edits, edit)
	}

	if len(edits) == 0 {
		http.Error(w, "Entry not found", http.StatusNotFound)
		return
	}

	tmpl := `<html><body><h1>Edits</h1><ul>{{range .}}<li>{{.ModifiedBy}}: {{.Summary}} at {{.ModifiedAt}}</li>{{end}}</ul></body></html>`
	t, err := template.New("edits").Parse(tmpl)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	t.Execute(w, edits)
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
		if strings.HasSuffix(r.URL.Path, "/edits") {
			getEntryEdits(w, r)
			return
		}
		switch r.Method {
		case http.MethodGet:
			getEntry(w, r)
		case http.MethodPut:
			updateEntry(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	log.Println("Server started at 0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}