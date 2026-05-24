package main

import (
	"encoding/json"
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"database/sql"
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
	Content   string `json:"content"`
	ModifiedBy string `json:"modifiedBy"`
	Summary   string `json:"summary"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create the entries table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS entries (
		id TEXT PRIMARY KEY,
		title TEXT,
		content TEXT,
		last_modified_by TEXT,
		last_modified_at TEXT
	)`)
	if err != nil {
		panic(err)
	}

	r := gin.Default()

	r.GET("/entries", getEntries)
	r.POST("/entries", createEntry)
	r.GET("/entries/:entryId", getEntry)
	r.PUT("/entries/:entryId", updateEntry)

	r.Run("0.0.0.0:5000")
}

func getEntries(c *gin.Context) {
	rows, err := db.Query("SELECT id, title FROM entries")
	if err != nil {
		c.String(http.StatusInternalServerError, "Error querying entries")
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
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	id := uuid.New().String()
	_, err := db.Exec("INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, "now()")
	if err != nil {
		c.String(http.StatusInternalServerError, "Error creating entry")
		return
	}

	entry := Entry{
		ID:             id,
		Title:          newEntry.Title,
		Content:        newEntry.Content,
		LastModifiedBy: newEntry.CreatedBy,
		LastModifiedAt: "now()",
	}
	c.JSON(http.StatusCreated, entry)
}

func getEntry(c *gin.Context) {
	entryId := c.Param("entryId")
	row := db.QueryRow("SELECT id, title, content, last_modified_by, last_modified_at FROM entries WHERE id = ?", entryId)

	var entry Entry
	if err := row.Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt); err != nil {
		if err == sql.ErrNoRows {
			c.String(http.StatusNotFound, "Entry not found")
		} else {
			c.String(http.StatusInternalServerError, "Error retrieving entry")
		}
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

	_, err := db.Exec("UPDATE entries SET content = ?, last_modified_by = ?, last_modified_at = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, "now()", entryId)
	if err != nil {
		c.String(http.StatusInternalServerError, "Error updating entry")
		return
	}

	c.String(http.StatusOK, "Entry updated successfully")
}