package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"regexp"
	"time"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Entry struct {
	ID            string `json:"id"`
	Title         string `json:"title"`
	Content       string `json:"content"`
	LastModifiedBy string `json:"lastModifiedBy"`
	LastModifiedAt string `json:"lastModifiedAt"`
}

type NewEntry struct {
	Title    string `json:"title"`
	Content  string `json:"content"`
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
		log.Fatal(err)
	}

	createEntriesTable := `
	CREATE TABLE IF NOT EXISTS entries (
		id TEXT PRIMARY KEY,
		title TEXT,
		content TEXT,
		lastModifiedBy TEXT,
		lastModifiedAt TEXT
	);`

	createEditsTable := `
	CREATE TABLE IF NOT EXISTS edits (
		id TEXT PRIMARY KEY,
		entryId TEXT,
		modifiedBy TEXT,
		summary TEXT,
		modifiedAt TEXT,
		FOREIGN KEY(entryId) REFERENCES entries(id)
	);`

	_, err = db.Exec(createEntriesTable)
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(createEditsTable)
	if err != nil {
		log.Fatal(err)
	}
}

func getEntriesHandler(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query("SELECT id, title FROM entries")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	type EntryLink struct {
		ID    string
		Title string
	}

	var entries []EntryLink
	for rows.Next() {
		var entry EntryLink
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

	w.Header().Set("Content-Type", "text/html")
	t.Execute(w, entries)
}

func createEntryHandler(w http.ResponseWriter, r *http.Request) {
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
		ID:            id,
		Title:         newEntry.Title,
		Content:       newEntry.Content,
		LastModifiedBy: newEntry.CreatedBy,
		LastModifiedAt: now,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(entry)
}

func getEntryHandler(w http.ResponseWriter, r *http.Request) {
	entryId := r.URL.Path[len("/entries/"):]

	if !isValidUUID(entryId) {
		http.Error(w, "Invalid entry ID format", http.StatusBadRequest)
		return
	}

	row := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId)

	var entry Entry
	if err := row.Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt); err != nil {
		http.Error(w, "Entry not found", http.StatusNotFound)
		return
	}

	tmpl := `<html><body><h1>{{.Title}}</h1><p>{{.Content}}</p><p>Last modified by: {{.LastModifiedBy}} at {{.LastModifiedAt}}</p></body></html>`
	t, err := template.New("entry").Parse(tmpl)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/html")
	t.Execute(w, entry)
}

func updateEntryHandler(w http.ResponseWriter, r *http.Request) {
	entryId := r.URL.Path[len("/entries/"):]

	if !isValidUUID(entryId) {
		http.Error(w, "Invalid entry ID format", http.StatusBadRequest)
		return
	}

	var updateEntry UpdateEntry
	if err := json.NewDecoder(r.Body).Decode(&updateEntry); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	now := time.Now().Format(time.RFC3339)

	res, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, now, entryId)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	rowsAffected, err := res.RowsAffected()
	if err != nil || rowsAffected == 0 {
		http.Error(w, "Entry not found", http.StatusNotFound)
		return
	}

	_, err = db.Exec("INSERT INTO edits (id, entryId, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?)",
		uuid.New().String(), entryId, updateEntry.ModifiedBy, updateEntry.Summary, now)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	entry := Entry{
		ID:            entryId,
		Content:       updateEntry.Content,
		LastModifiedBy: updateEntry.ModifiedBy,
		LastModifiedAt: now,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(entry)
}

func getEntryEditsHandler(w http.ResponseWriter, r *http.Request) {
	entryId := r.URL.Path[len("/entries/"):len("/entries/")+36]

	if !isValidUUID(entryId) {
		http.Error(w, "Invalid entry ID format", http.StatusBadRequest)
		return
	}

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

	w.Header().Set("Content-Type", "text/html")
	t.Execute(w, edits)
}

func isValidUUID(u string) bool {
	r := regexp.MustCompile(`^[a-fA-F0-9-]{36}$`)
	return r.MatchString(u)
}

func main() {
	initDB()
	defer db.Close()

	mux := http.NewServeMux()

	mux.HandleFunc("/entries", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			getEntriesHandler(w, r)
		case http.MethodPost:
			createEntryHandler(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	mux.HandleFunc("/entries/", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			if len(r.URL.Path) > len("/entries/")+36 {
				getEntryEditsHandler(w, r)
			} else {
				getEntryHandler(w, r)
			}
		case http.MethodPut:
			updateEntryHandler(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	log.Println("Server started at 0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", mux))
}