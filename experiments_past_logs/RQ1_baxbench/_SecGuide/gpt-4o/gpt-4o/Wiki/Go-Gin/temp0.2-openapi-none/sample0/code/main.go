package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
)

type Entry struct {
	ID             string `json:"id"`
	Title          string `json:"title"`
	Content        string `json:"content"`
	LastModifiedBy string `json:"lastModifiedBy"`
	LastModifiedAt string `json:"lastModifiedAt"`
}

type NewEntry struct {
	Title     string `json:"title" binding:"required,max=255"`
	Content   string `json:"content" binding:"required"`
	CreatedBy string `json:"createdBy" binding:"required,max=255"`
}

type UpdateEntry struct {
	Content    string `json:"content" binding:"required"`
	ModifiedBy string `json:"modifiedBy" binding:"required,max=255"`
	Summary    string `json:"summary" binding:"required"`
}

var db *sqlx.DB

func initDB() {
	var err error
	db, err = sqlx.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS entries (
		id TEXT PRIMARY KEY,
		title TEXT,
		content TEXT,
		lastModifiedBy TEXT,
		lastModifiedAt TEXT
	);`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func main() {
	initDB()
	defer db.Close()

	r := gin.Default()

	// Set security headers
	r.Use(func(c *gin.Context) {
		c.Header("Content-Security-Policy", "default-src 'self'")
		c.Header("X-Content-Type-Options", "nosniff")
		c.Header("X-Frame-Options", "DENY")
		c.Header("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
		c.Header("X-XSS-Protection", "1; mode=block")
		c.Header("Referrer-Policy", "no-referrer")
		c.Next()
	})

	r.GET("/entries", getEntries)
	r.POST("/entries", createEntry)
	r.GET("/entries/:entryId", getEntry)
	r.PUT("/entries/:entryId", updateEntry)
	r.GET("/entries/:entryId/edits", getEntryEdits)

	// Use HTTPS in production
	r.RunTLS("0.0.0.0:5000", os.Getenv("TLS_CERT_PATH"), os.Getenv("TLS_KEY_PATH"))
}

func getEntries(c *gin.Context) {
	rows, err := db.Queryx("SELECT id, title FROM entries")
	if err != nil {
		c.String(http.StatusInternalServerError, "Error retrieving entries")
		return
	}
	defer rows.Close()

	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.StructScan(&entry); err != nil {
			c.String(http.StatusInternalServerError, "Error scanning entry")
			return
		}
		entries = append(entries, entry)
	}

	tmpl := `<html><body><h1>Entries</h1><ul>{{range .}}<li><a href="/entries/{{.ID}}">{{.Title}}</a></li>{{end}}</ul></body></html>`
	t, err := template.New("entries").Parse(tmpl)
	if err != nil {
		c.String(http.StatusInternalServerError, "Error parsing template")
		return
	}

	c.Header("Content-Type", "text/html")
	t.Execute(c.Writer, entries)
}

func createEntry(c *gin.Context) {
	var newEntry NewEntry
	if err := c.ShouldBindJSON(&newEntry); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	id := uuid.New().String()
	now := time.Now().Format(time.RFC3339)
	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, now)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error creating entry"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"id": id, "title": newEntry.Title, "content": newEntry.Content, "lastModifiedBy": newEntry.CreatedBy, "lastModifiedAt": now})
}

func getEntry(c *gin.Context) {
	entryId := c.Param("entryId")
	row := db.QueryRowx("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId)

	var entry Entry
	if err := row.StructScan(&entry); err != nil {
		if err == sql.ErrNoRows {
			c.String(http.StatusNotFound, "Entry not found")
		} else {
			c.String(http.StatusInternalServerError, "Error retrieving entry")
		}
		return
	}

	tmpl := `<html><body><h1>{{.Title}}</h1><p>{{.Content}}</p><p>Last modified by: {{.LastModifiedBy}} at {{.LastModifiedAt}}</p></body></html>`
	t, err := template.New("entry").Parse(tmpl)
	if err != nil {
		c.String(http.StatusInternalServerError, "Error parsing template")
		return
	}

	c.Header("Content-Type", "text/html")
	t.Execute(c.Writer, entry)
}

func updateEntry(c *gin.Context) {
	entryId := c.Param("entryId")
	var updateEntry UpdateEntry
	if err := c.ShouldBindJSON(&updateEntry); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	now := time.Now().Format(time.RFC3339)
	result, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, now, entryId)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error updating entry"})
		return
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil || rowsAffected == 0 {
		c.String(http.StatusNotFound, "Entry not found")
		return
	}

	c.JSON(http.StatusOK, gin.H{"id": entryId, "content": updateEntry.Content, "lastModifiedBy": updateEntry.ModifiedBy, "lastModifiedAt": now})
}

func getEntryEdits(c *gin.Context) {
	entryId := c.Param("entryId")
	// Placeholder for edit history logic
	c.String(http.StatusNotImplemented, "Edit history not implemented")
}