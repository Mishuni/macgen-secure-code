package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
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
	Title     string `json:"title" binding:"required"`
	Content   string `json:"content" binding:"required"`
	CreatedBy string `json:"createdBy" binding:"required"`
}

type UpdateEntry struct {
	Content    string `json:"content" binding:"required"`
	ModifiedBy string `json:"modifiedBy" binding:"required"`
	Summary    string `json:"summary" binding:"required"`
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
	router := gin.Default()

	router.GET("/entries", getEntries)
	router.POST("/entries", createEntry)
	router.GET("/entries/:entryId", getEntry)
	router.PUT("/entries/:entryId", updateEntry)

	router.Run("0.0.0.0:5000")
}

func getEntries(c *gin.Context) {
	rows, err := db.Query("SELECT id, title FROM entries")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch entries"})
		return
	}
	defer rows.Close()

	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to scan entry"})
			return
		}
		entries = append(entries, entry)
	}

	c.JSON(http.StatusOK, entries)
}

func createEntry(c *gin.Context) {
	var newEntry NewEntry
	if err := c.ShouldBindJSON(&newEntry); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	id := uuid.New().String()
	lastModifiedAt := time.Now().Format(time.RFC3339)
	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, lastModifiedAt)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create entry"})
		return
	}

	entry := Entry{
		ID:             id,
		Title:          newEntry.Title,
		Content:        newEntry.Content,
		LastModifiedBy: newEntry.CreatedBy,
		LastModifiedAt: lastModifiedAt,
	}
	c.JSON(http.StatusCreated, entry)
}

func getEntry(c *gin.Context) {
	entryId := c.Param("entryId")
	var entry Entry
	err := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId).Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Entry not found"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch entry"})
		}
		return
	}

	c.JSON(http.StatusOK, entry)
}

func updateEntry(c *gin.Context) {
	entryId := c.Param("entryId")
	var updateEntry UpdateEntry
	if err := c.ShouldBindJSON(&updateEntry); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	lastModifiedAt := time.Now().Format(time.RFC3339)
	_, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, lastModifiedAt, entryId)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Entry not found"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update entry"})
		}
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Entry updated successfully"})
}