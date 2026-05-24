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

func main() {
	// Initialize the database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	// Initialize the Gin router
	router := gin.Default()

	// Routes
	router.GET("/entries", func(c *gin.Context) {
		getEntriesHandler(c, db)
	})
	router.POST("/entries", func(c *gin.Context) {
		createEntryHandler(c, db)
	})
	router.GET("/entries/:entryId", func(c *gin.Context) {
		getEntryHandler(c, db)
	})
	router.PUT("/entries/:entryId", func(c *gin.Context) {
		updateEntryHandler(c, db)
	})
	router.GET("/entries/:entryId/edits", func(c *gin.Context) {
		getEditsHandler(c, db)
	})

	// Start the server
	log.Println("Starting server on 0.0.0.0:5000")
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
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
			modified_at TEXT NOT NULL,
			FOREIGN KEY(entry_id) REFERENCES entries(id)
		);
	`)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}

func getEntriesHandler(c *gin.Context, db *sql.DB) {
	rows, err := db.Query("SELECT id, title FROM entries")
	if err != nil {
		c.String(http.StatusInternalServerError, "Failed to fetch entries")
		return
	}
	defer rows.Close()

	var entries []map[string]string
	for rows.Next() {
		var id, title string
		if err := rows.Scan(&id, &title); err != nil {
			c.String(http.StatusInternalServerError, "Failed to parse entries")
			return
		}
		entries = append(entries, map[string]string{
			"id":    id,
			"title": title,
		})
	}

	c.JSON(http.StatusOK, entries)
}

func createEntryHandler(c *gin.Context, db *sql.DB) {
	var newEntry struct {
		Title     string `json:"title" binding:"required"`
		Content   string `json:"content" binding:"required"`
		CreatedBy string `json:"createdBy" binding:"required"`
	}

	if err := c.ShouldBindJSON(&newEntry); err != nil {
		c.String(http.StatusBadRequest, "Invalid request body")
		return
	}

	id := uuid.New().String()
	now := time.Now().Format(time.RFC3339)

	_, err := db.Exec(
		"INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, now,
	)
	if err != nil {
		c.String(http.StatusInternalServerError, "Failed to create entry")
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"id":      id,
		"title":   newEntry.Title,
		"content": newEntry.Content,
	})
}

func getEntryHandler(c *gin.Context, db *sql.DB) {
	entryId := c.Param("entryId")

	var entry struct {
		ID             string
		Title          string
		Content        string
		LastModifiedBy string
		LastModifiedAt string
	}

	err := db.QueryRow(
		"SELECT id, title, content, last_modified_by, last_modified_at FROM entries WHERE id = ?",
		entryId,
	).Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)

	if err == sql.ErrNoRows {
		c.String(http.StatusNotFound, "Entry not found")
		return
	} else if err != nil {
		c.String(http.StatusInternalServerError, "Failed to fetch entry")
		return
	}

	c.JSON(http.StatusOK, entry)
}

func updateEntryHandler(c *gin.Context, db *sql.DB) {
	entryId := c.Param("entryId")

	var updateEntry struct {
		Content    string `json:"content" binding:"required"`
		ModifiedBy string `json:"modifiedBy" binding:"required"`
		Summary    string `json:"summary" binding:"required"`
	}

	if err := c.ShouldBindJSON(&updateEntry); err != nil {
		c.String(http.StatusBadRequest, "Invalid request body")
		return
	}

	now := time.Now().Format(time.RFC3339)

	tx, err := db.Begin()
	if err != nil {
		c.String(http.StatusInternalServerError, "Failed to update entry")
		return
	}

	_, err = tx.Exec(
		"UPDATE entries SET content = ?, last_modified_by = ?, last_modified_at = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, now, entryId,
	)
	if err != nil {
		tx.Rollback()
		c.String(http.StatusInternalServerError, "Failed to update entry")
		return
	}

	editId := uuid.New().String()
	_, err = tx.Exec(
		"INSERT INTO edits (id, entry_id, modified_by, summary, modified_at) VALUES (?, ?, ?, ?, ?)",
		editId, entryId, updateEntry.ModifiedBy, updateEntry.Summary, now,
	)
	if err != nil {
		tx.Rollback()
		c.String(http.StatusInternalServerError, "Failed to log edit")
		return
	}

	if err := tx.Commit(); err != nil {
		c.String(http.StatusInternalServerError, "Failed to commit transaction")
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "Entry updated successfully",
	})
}

func getEditsHandler(c *gin.Context, db *sql.DB) {
	entryId := c.Param("entryId")

	rows, err := db.Query(
		"SELECT id, modified_by, summary, modified_at FROM edits WHERE entry_id = ?",
		entryId,
	)
	if err != nil {
		c.String(http.StatusInternalServerError, "Failed to fetch edits")
		return
	}
	defer rows.Close()

	var edits []map[string]string
	for rows.Next() {
		var id, modifiedBy, summary, modifiedAt string
		if err := rows.Scan(&id, &modifiedBy, &summary, &modifiedAt); err != nil {
			c.String(http.StatusInternalServerError, "Failed to parse edits")
			return
		}
		edits = append(edits, map[string]string{
			"id":          id,
			"modifiedBy":  modifiedBy,
			"summary":     summary,
			"modifiedAt":  modifiedAt,
		})
	}

	c.JSON(http.StatusOK, edits)
}