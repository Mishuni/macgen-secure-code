package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
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

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	createTable()

	r := gin.Default()
	r.GET("/entries", getEntries)
	r.POST("/entries", createEntry)
	r.GET("/entries/:entryId", getEntry)
	r.PUT("/entries/:entryId", updateEntry)
	r.GET("/entries/:entryId/edits", getEntryEdits)

	r.Run("0.0.0.0:5000")
}

func createTable() {
	query := `CREATE TABLE IF NOT EXISTS entries (
		id TEXT PRIMARY KEY,
		title TEXT,
		content TEXT,
		lastModifiedBy TEXT,
		lastModifiedAt DATETIME
	);`
	_, err := db.Exec(query)
	if err != nil {
		panic(err)
	}
}

func getEntries(c *gin.Context) {
	rows, err := db.Query("SELECT id, title FROM entries")
	if err != nil {
		c.String(http.StatusInternalServerError, "Error fetching entries")
		return
	}
	defer rows.Close()

	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
			c.String(http.StatusInternalServerError, "Error scanning entry")
			return
		}
		entries = append(entries, entry)
	}

	c.JSON(http.StatusOK, entries)
}

func createEntry(c *gin.Context) {
	var newEntry NewEntry
	if err := c.ShouldBindJSON(&newEntry); err != nil {
		c.JSON(http.StatusBadRequest, err.Error())
		return
	}

	id := uuid.New().String()
	now := time.Now().Format(time.RFC3339)
	entry := Entry{
		ID:             id,
		Title:          newEntry.Title,
		Content:        newEntry.Content,
		LastModifiedBy: newEntry.CreatedBy,
		LastModifiedAt: now,
	}

	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		entry.ID, entry.Title, entry.Content, entry.LastModifiedBy, entry.LastModifiedAt)
	if err != nil {
		c.String(http.StatusInternalServerError, "Error creating entry")
		return
	}

	c.JSON(http.StatusCreated, entry)
}

func getEntry(c *gin.Context) {
	entryId := c.Param("entryId")
	var entry Entry
	err := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId).Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			c.String(http.StatusNotFound, "Entry not found")
			return
		}
		c.String(http.StatusInternalServerError, "Error fetching entry")
		return
	}

	c.JSON(http.StatusOK, entry)
}

func updateEntry(c *gin.Context) {
	entryId := c.Param("entryId")
	var updateEntry UpdateEntry
	if err := c.ShouldBindJSON(&updateEntry); err != nil {
		c.JSON(http.StatusBadRequest, err.Error())
		return
	}

	now := time.Now().Format(time.RFC3339)
	_, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, now, entryId)
	if err != nil {
		if err == sql.ErrNoRows {
			c.String(http.StatusNotFound, "Entry not found")
			return
		}
		c.String(http.StatusInternalServerError, "Error updating entry")
		return
	}

	entry, _ := getEntryById(entryId)
	c.JSON(http.StatusOK, entry)
}

func getEntryById(entryId string) (Entry, error) {
	var entry Entry
	err := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId).Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)
	return entry, err
}

func getEntryEdits(c *gin.Context) {
	entryId := c.Param("entryId")
	c.String(http.StatusOK, "Edit history for entry ID: "+entryId)
}