package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
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
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		logError(err)
		return
	}
	defer db.Close()

	createTable()

	router := gin.Default()
	router.GET("/entries", getEntries)
	router.POST("/entries", createEntry)
	router.GET("/entries/:entryId", getEntry)
	router.PUT("/entries/:entryId", updateEntry)

	router.Run("0.0.0.0:5000")
}

func createTable() {
	query := `CREATE TABLE IF NOT EXISTS entries (
		id TEXT PRIMARY KEY,
		title TEXT NOT NULL,
		content TEXT NOT NULL,
		lastModifiedBy TEXT NOT NULL,
		lastModifiedAt DATETIME NOT NULL
	);`
	_, err := db.Exec(query)
	if err != nil {
		logError(err)
	}
}

func getEntries(c *gin.Context) {
	rows, err := db.Query("SELECT id, title FROM entries")
	if err != nil {
		logError(err)
		c.String(http.StatusInternalServerError, "Error fetching entries")
		return
	}
	defer rows.Close()

	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
			logError(err)
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
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	if len(newEntry.Title) == 0 || len(newEntry.Content) == 0 {
		c.String(http.StatusBadRequest, "Title and Content cannot be empty")
		return
	}

	id := uuid.New().String()
	now := time.Now().Format(time.RFC3339)
	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, now)
	if err != nil {
		logError(err)
		c.String(http.StatusInternalServerError, "Error creating entry")
		return
	}

	c.JSON(http.StatusCreated, Entry{ID: id, Title: newEntry.Title, Content: newEntry.Content, LastModifiedBy: newEntry.CreatedBy, LastModifiedAt: now})
}

func getEntry(c *gin.Context) {
	entryId := c.Param("entryId")
	row := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId)

	var entry Entry
	if err := row.Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt); err != nil {
		if err == sql.ErrNoRows {
			c.String(http.StatusNotFound, "Entry not found")
			return
		}
		logError(err)
		c.String(http.StatusInternalServerError, "Error fetching entry")
		return
	}

	c.JSON(http.StatusOK, entry)
}

func updateEntry(c *gin.Context) {
	entryId := c.Param("entryId")
	var updateEntry UpdateEntry
	if err := c.ShouldBindJSON(&updateEntry); err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	if len(updateEntry.Content) == 0 {
		c.String(http.StatusBadRequest, "Content cannot be empty")
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
		logError(err)
		c.String(http.StatusInternalServerError, "Error updating entry")
		return
	}

	c.JSON(http.StatusOK, Entry{ID: entryId, Title: updateEntry.Content, LastModifiedBy: updateEntry.ModifiedBy, LastModifiedAt: now})
}

func logError(err error) {
	// Log the error to the console or a logging system
	fmt.Println("Error:", err)
}