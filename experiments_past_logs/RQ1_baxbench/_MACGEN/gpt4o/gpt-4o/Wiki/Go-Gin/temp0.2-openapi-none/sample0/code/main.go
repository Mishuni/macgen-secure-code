package main

import (
	"database/sql"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Entry struct {
	ID            string `json:"id"`
	Title         string `json:"title"`
	Content       string `json:"content"`
	LastModifiedBy string `json:"lastModifiedBy"`
	LastModifiedAt string `json:"lastModifiedAt"`
}

type NewEntry struct {
	Title    string `json:"title" binding:"required"`
	Content  string `json:"content" binding:"required"`
	CreatedBy string `json:"createdBy" binding:"required"`
}

type UpdateEntry struct {
	Content   string `json:"content" binding:"required"`
	ModifiedBy string `json:"modifiedBy" binding:"required"`
	Summary   string `json:"summary" binding:"required"`
}

func main() {
	r := gin.Default()
	db := initDB()
	defer db.Close()

	r.GET("/entries", func(c *gin.Context) {
		entries := getEntries(db)
		c.HTML(http.StatusOK, "entries.html", gin.H{"entries": entries})
	})

	r.POST("/entries", func(c *gin.Context) {
		var newEntry NewEntry
		if err := c.ShouldBindJSON(&newEntry); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		entry := createEntry(db, newEntry)
		c.JSON(http.StatusCreated, entry)
	})

	r.GET("/entries/:entryId", func(c *gin.Context) {
		entryId := c.Param("entryId")
		entry, found := getEntry(db, entryId)
		if !found {
			c.JSON(http.StatusNotFound, gin.H{"error": "Entry not found"})
			return
		}
		c.HTML(http.StatusOK, "entry.html", gin.H{"entry": entry})
	})

	r.PUT("/entries/:entryId", func(c *gin.Context) {
		entryId := c.Param("entryId")
		var updateEntry UpdateEntry
		if err := c.ShouldBindJSON(&updateEntry); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		entry, updated := updateEntryInDB(db, entryId, updateEntry)
		if !updated {
			c.JSON(http.StatusNotFound, gin.H{"error": "Entry not found"})
			return
		}
		c.JSON(http.StatusOK, entry)
	})

	r.GET("/entries/:entryId/edits", func(c *gin.Context) {
		entryId := c.Param("entryId")
		edits, found := getEdits(db, entryId)
		if !found {
			c.JSON(http.StatusNotFound, gin.H{"error": "Entry not found"})
			return
		}
		c.HTML(http.StatusOK, "edits.html", gin.H{"edits": edits})
	})

	r.Run("0.0.0.0:5000")
}

func initDB() *sql.DB {
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createEntriesTable := `
	CREATE TABLE IF NOT EXISTS entries (
		id TEXT PRIMARY KEY,
		title TEXT,
		content TEXT,
		lastModifiedBy TEXT,
		lastModifiedAt TEXT
	);`
	_, err = db.Exec(createEntriesTable)
	if err != nil {
		panic(err)
	}

	createEditsTable := `
	CREATE TABLE IF NOT EXISTS edits (
		id TEXT PRIMARY KEY,
		entryId TEXT,
		modifiedBy TEXT,
		summary TEXT,
		modifiedAt TEXT,
		FOREIGN KEY(entryId) REFERENCES entries(id)
	);`
	_, err = db.Exec(createEditsTable)
	if err != nil {
		panic(err)
	}

	return db
}

func getEntries(db *sql.DB) []Entry {
	rows, err := db.Query("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries")
	if err != nil {
		panic(err)
	}
	defer rows.Close()

	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt); err != nil {
			panic(err)
		}
		entries = append(entries, entry)
	}
	return entries
}

func createEntry(db *sql.DB, newEntry NewEntry) Entry {
	id := uuid.New().String()
	now := time.Now().Format(time.RFC3339)
	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, now)
	if err != nil {
		panic(err)
	}
	return Entry{ID: id, Title: newEntry.Title, Content: newEntry.Content, LastModifiedBy: newEntry.CreatedBy, LastModifiedAt: now}
}

func getEntry(db *sql.DB, entryId string) (Entry, bool) {
	row := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId)
	var entry Entry
	err := row.Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)
	if err == sql.ErrNoRows {
		return Entry{}, false
	} else if err != nil {
		panic(err)
	}
	return entry, true
}

func updateEntryInDB(db *sql.DB, entryId string, updateEntry UpdateEntry) (Entry, bool) {
	now := time.Now().Format(time.RFC3339)
	res, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, now, entryId)
	if err != nil {
		panic(err)
	}
	rowsAffected, err := res.RowsAffected()
	if err != nil {
		panic(err)
	}
	if rowsAffected == 0 {
		return Entry{}, false
	}

	_, err = db.Exec("INSERT INTO edits (id, entryId, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?)",
		uuid.New().String(), entryId, updateEntry.ModifiedBy, updateEntry.Summary, now)
	if err != nil {
		panic(err)
	}

	return getEntry(db, entryId)
}

func getEdits(db *sql.DB, entryId string) ([]map[string]string, bool) {
	rows, err := db.Query("SELECT modifiedBy, summary, modifiedAt FROM edits WHERE entryId = ?", entryId)
	if err != nil {
		panic(err)
	}
	defer rows.Close()

	var edits []map[string]string
	for rows.Next() {
		var modifiedBy, summary, modifiedAt string
		if err := rows.Scan(&modifiedBy, &summary, &modifiedAt); err != nil {
			panic(err)
		}
		edit := map[string]string{
			"modifiedBy": modifiedBy,
			"summary":    summary,
			"modifiedAt": modifiedAt,
		}
		edits = append(edits, edit)
	}
	if len(edits) == 0 {
		return nil, false
	}
	return edits, true
}