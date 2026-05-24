package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
	"html"

	"github.com/gin-gonic/gin"
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

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	createTable := `
	CREATE TABLE IF NOT EXISTS entries (
		id TEXT PRIMARY KEY,
		title TEXT,
		content TEXT,
		lastModifiedBy TEXT,
		lastModifiedAt TEXT
	);`
	_, err = db.Exec(createTable)
	if err != nil {
		panic(err)
	}
}

func validateEntry(title, content string) bool {
	return len(title) <= 100 && len(content) <= 1000
}

func getEntries(c *gin.Context) {
	rows, err := db.Query("SELECT id, title FROM entries")
	if err != nil {
		c.String(http.StatusInternalServerError, "An error occurred")
		return
	}
	defer rows.Close()

	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
			c.String(http.StatusInternalServerError, "An error occurred")
			return
		}
		entries = append(entries, entry)
	}

	c.HTML(http.StatusOK, "entries.html", entries)
}

func createEntry(c *gin.Context) {
	var newEntry NewEntry
	if err := c.ShouldBindJSON(&newEntry); err != nil || !validateEntry(newEntry.Title, newEntry.Content) {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	newEntry.Title = html.EscapeString(newEntry.Title)
	newEntry.Content = html.EscapeString(newEntry.Content)

	id := uuid.New().String()
	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, time.Now().Format(time.RFC3339))
	if err != nil {
		c.String(http.StatusInternalServerError, "An error occurred")
		return
	}

	entry := Entry{ID: id, Title: newEntry.Title, Content: newEntry.Content, LastModifiedBy: newEntry.CreatedBy, LastModifiedAt: time.Now().Format(time.RFC3339)}
	c.JSON(http.StatusCreated, entry)
}

func getEntry(c *gin.Context) {
	entryId := c.Param("entryId")
	row := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId)

	var entry Entry
	if err := row.Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt); err != nil {
		c.String(http.StatusNotFound, "Entry not found")
		return
	}

	c.HTML(http.StatusOK, "entry.html", entry)
}

func updateEntry(c *gin.Context) {
	entryId := c.Param("entryId")
	var updateEntry UpdateEntry
	if err := c.ShouldBindJSON(&updateEntry); err != nil || len(updateEntry.Content) == 0 {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	updateEntry.Content = html.EscapeString(updateEntry.Content)

	_, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, time.Now().Format(time.RFC3339), entryId)
	if err != nil {
		c.String(http.StatusNotFound, "Entry not found")
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Entry updated successfully"})
}

func getEntryEdits(c *gin.Context) {
	entryId := c.Param("entryId")
	// Placeholder for edit history, as no edit tracking is implemented
	c.String(http.StatusOK, "Edit history for entry: "+entryId)
}

func main() {
	r := gin.Default()
	r.GET("/entries", getEntries)
	r.POST("/entries", createEntry)
	r.GET("/entries/:entryId", getEntry)
	r.PUT("/entries/:entryId", updateEntry)
	r.GET("/entries/:entryId/edits", getEntryEdits)
	r.Run("0.0.0.0:5000")
}