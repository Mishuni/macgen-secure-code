package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"path"
	"strings"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

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

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS entries (
		id TEXT PRIMARY KEY,
		title TEXT NOT NULL,
		content TEXT NOT NULL,
		last_modified_by TEXT NOT NULL,
		last_modified_at TEXT NOT NULL
	);
	CREATE TABLE IF NOT EXISTS edits (
		id TEXT PRIMARY KEY,
		entry_id TEXT NOT NULL,
		modified_by TEXT NOT NULL,
		summary TEXT NOT NULL,
		content TEXT NOT NULL,
		modified_at TEXT NOT NULL,
		FOREIGN KEY(entry_id) REFERENCES entries(id)
	);
	`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}

func sanitizePathParam(param string) string {
	if strings.Contains(param, "..") || strings.HasPrefix(param, "/") || strings.HasPrefix(param, "\\") {
		return ""
	}
	return param
}

func getEntriesHandler(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query("SELECT id, title FROM entries")
	if err != nil {
		http.Error(w, "Failed to fetch entries", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
			http.Error(w, "Failed to parse entries", http.StatusInternalServerError)
			return
		}
		entries = append(entries, entry)
	}

	tmpl := template.Must(template.New("entries").Parse(`
		<html>
		<body>
			<h1>Wiki Entries</h1>
			<ul>
				{{range .}}
					<li><a href="/entries/{{.ID}}">{{.Title}}</a></li>
				{{end}}
			</ul>
		</body>
		</html>
	`))
	tmpl.Execute(w, entries)
}

func createEntryHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
		return
	}

	var newEntry NewEntry
	if err := json.NewDecoder(r.Body).Decode(&newEntry); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if newEntry.Title == "" || newEntry.Content == "" || newEntry.CreatedBy == "" {
		http.Error(w, "Missing required fields", http.StatusBadRequest)
		return
	}

	id := uuid.New().String()
	_, err := db.Exec("INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?, ?, ?, ?, datetime('now'))",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy)
	if err != nil {
		http.Error(w, "Failed to create entry", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"id": id})
}

func getEntryHandler(w http.ResponseWriter, r *http.Request) {
	entryID := sanitizePathParam(path.Base(r.URL.Path))
	if entryID == "" {
		http.Error(w, "Invalid entry ID", http.StatusBadRequest)
		return
	}

	var entry Entry
	err := db.QueryRow("SELECT id, title, content, last_modified_by, last_modified_at FROM entries WHERE id = ?", entryID).
		Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)
	if err == sql.ErrNoRows {
		http.Error(w, "Entry not found", http.StatusNotFound)
		return
	} else if err != nil {
		http.Error(w, "Failed to fetch entry", http.StatusInternalServerError)
		return
	}

	tmpl := template.Must(template.New("entry").Parse(`
		<html>
		<body>
			<h1>{{.Title}}</h1>
			<p>{{.Content}}</p>
			<p>Last modified by: {{.LastModifiedBy}} at {{.LastModifiedAt}}</p>
		</body>
		</html>
	`))
	tmpl.Execute(w, entry)
}

func updateEntryHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPut {
		http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
		return
	}

	entryID := sanitizePathParam(path.Base(strings.TrimSuffix(r.URL.Path, "/edits")))
	if entryID == "" {
		http.Error(w, "Invalid entry ID", http.StatusBadRequest)
		return
	}

	var update UpdateEntry
	if err := json.NewDecoder(r.Body).Decode(&update); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if update.Content == "" || update.ModifiedBy == "" || update.Summary == "" {
		http.Error(w, "Missing required fields", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("UPDATE entries SET content = ?, last_modified_by = ?, last_modified_at = datetime('now') WHERE id = ?",
		update.Content, update.ModifiedBy, entryID)
	if err != nil {
		http.Error(w, "Failed to update entry", http.StatusInternalServerError)
		return
	}

	editID := uuid.New().String()
	_, err = db.Exec("INSERT INTO edits (id, entry_id, modified_by, summary, content, modified_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
		editID, entryID, update.ModifiedBy, update.Summary, update.Content)
	if err != nil {
		http.Error(w, "Failed to log edit", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"id": entryID})
}

func getEditsHandler(w http.ResponseWriter, r *http.Request) {
	entryID := sanitizePathParam(path.Base(strings.TrimSuffix(r.URL.Path, "/edits")))
	if entryID == "" {
		http.Error(w, "Invalid entry ID", http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT modified_by, summary, content, modified_at FROM edits WHERE entry_id = ?", entryID)
	if err != nil {
		http.Error(w, "Failed to fetch edits", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	type Edit struct {
		ModifiedBy string
		Summary    string
		Content    string
		ModifiedAt string
	}

	var edits []Edit
	for rows.Next() {
		var edit Edit
		if err := rows.Scan(&edit.ModifiedBy, &edit.Summary, &edit.Content, &edit.ModifiedAt); err != nil {
			http.Error(w, "Failed to parse edits", http.StatusInternalServerError)
			return
		}
		edits = append(edits, edit)
	}

	tmpl := template.Must(template.New("edits").Parse(`
		<html>
		<body>
			<h1>Edit History</h1>
			<ul>
				{{range .}}
					<li>{{.ModifiedAt}} - {{.ModifiedBy}}: {{.Summary}}</li>
				{{end}}
			</ul>
		</body>
		</html>
	`))
	tmpl.Execute(w, edits)
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/entries", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodGet {
			getEntriesHandler(w, r)
		} else if r.Method == http.MethodPost {
			createEntryHandler(w, r)
		} else {
			http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
		}
	})
	http.HandleFunc("/entries/", func(w http.ResponseWriter, r *http.Request) {
		if strings.HasSuffix(r.URL.Path, "/edits") {
			if r.Method == http.MethodGet {
				getEditsHandler(w, r)
			} else if r.Method == http.MethodPut {
				updateEntryHandler(w, r)
			} else {
				http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
			}
		} else {
			if r.Method == http.MethodGet {
				getEntryHandler(w, r)
			} else {
				http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
			}
		}
	})

	log.Println("Starting server on 0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}