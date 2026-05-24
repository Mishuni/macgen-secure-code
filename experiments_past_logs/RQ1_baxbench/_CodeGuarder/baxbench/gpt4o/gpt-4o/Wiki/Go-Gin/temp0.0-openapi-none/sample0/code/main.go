package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Entry struct {
	ID             string `json:"id"`
	Title          string `json:"title"`
	Content        string `json:"content"`
	LastModifiedBy string `json:"lastModifiedBy"`
	LastModifiedAt string `json:"lastModifiedAt"`
}

type NewEntry struct {
	Title     string `json:"title" binding:"required"`
	Content   string `json:"content" binding:"required"`
	CreatedBy string `json:"createdBy" binding:"required"`
}

type UpdateEntry struct {
	Content   string `json:"content" binding:"required"`
	ModifiedBy string `json:"modifiedBy" binding:"required"`
	Summary   string `json:"summary" binding:"required"`
}

func main() {
	r := gin.Default()

	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Initialize database
	initDB(db)

	r.GET("/entries", func(c *gin.Context) {
		entries, err := getAllEntries(db)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve entries"})
			return
		}
		c.JSON(http.StatusOK, entries)
	})

	r.POST("/entries", func(c *gin.Context) {
		var newEntry NewEntry
		if err := c.ShouldBindJSON(&newEntry); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		entry, err := createEntry(db, newEntry)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create entry"})
			return
		}
		c.JSON(http.StatusCreated, entry)
	})

	r.GET("/entries/:entryId", func(c *gin.Context) {
		entryId := c.Param("entryId")
		entry, err := getEntry(db, entryId)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Entry not found"})
			return
		}
		c.JSON(http.StatusOK, entry)
	})

	r.PUT("/entries/:entryId", func(c *gin.Context) {
		entryId := c.Param("entryId")
		var updateEntry UpdateEntry
		if err := c.ShouldBindJSON(&updateEntry); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		entry, err := updateEntryContent(db, entryId, updateEntry)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Entry not found"})
			return
		}
		c.JSON(http.StatusOK, entry)
	})

	r.GET("/entries/:entryId/edits", func(c *gin.Context) {
		entryId := c.Param("entryId")
		edits, err := getEntryEdits(db, entryId)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Entry not found"})
			return
		}
		c.JSON(http.StatusOK, edits)
	})

	r.Run("0.0.0.0:5000")
}

func initDB(db *sql.DB) {
	createEntriesTableSQL := `CREATE TABLE IF NOT EXISTS entries (
		"id" TEXT NOT NULL PRIMARY KEY,
		"title" TEXT,
		"content" TEXT,
		"lastModifiedBy" TEXT,
		"lastModifiedAt" TEXT
	);`

	_, err := db.Exec(createEntriesTableSQL)
	if err != nil {
		log.Fatalf("Failed to create entries table: %v", err)
	}
}

func getAllEntries(db *sql.DB) ([]Entry, error) {
	rows, err := db.Query("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt); err != nil {
			return nil, err
		}
		entries = append(entries, entry)
	}
	return entries, nil
}

func createEntry(db *sql.DB, newEntry NewEntry) (Entry, error) {
	id := uuid.New().String()
	now := time.Now().Format(time.RFC3339)

	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, now)
	if err != nil {
		return Entry{}, err
	}

	return Entry{
		ID:             id,
		Title:          newEntry.Title,
		Content:        newEntry.Content,
		LastModifiedBy: newEntry.CreatedBy,
		LastModifiedAt: now,
	}, nil
}

func getEntry(db *sql.DB, entryId string) (Entry, error) {
	row := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId)

	var entry Entry
	if err := row.Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt); err != nil {
		return Entry{}, err
	}
	return entry, nil
}

func updateEntryContent(db *sql.DB, entryId string, updateEntry UpdateEntry) (Entry, error) {
	now := time.Now().Format(time.RFC3339)

	_, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, now, entryId)
	if err != nil {
		return Entry{}, err
	}

	return getEntry(db, entryId)
}

func getEntryEdits(db *sql.DB, entryId string) ([]Entry, error) {
	// Placeholder for edit history logic
	// For now, just return the current entry as a single "edit"
	entry, err := getEntry(db, entryId)
	if err != nil {
		return nil, err
	}
	return []Entry{entry}, nil
}