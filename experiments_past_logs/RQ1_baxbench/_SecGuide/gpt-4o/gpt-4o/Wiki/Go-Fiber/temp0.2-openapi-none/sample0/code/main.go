package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
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
	Title     string `json:"title"`
	Content   string `json:"content"`
	CreatedBy string `json:"createdBy"`
}

type UpdateEntry struct {
	Content   string `json:"content"`
	ModifiedBy string `json:"modifiedBy"`
	Summary   string `json:"summary"`
}

func main() {
	app := fiber.New()

	dbFileName := os.Getenv("DB_FILE_NAME")
	if dbFileName == "" {
		dbFileName = "db.sqlite3"
	}

	db, err := sql.Open("sqlite3", dbFileName)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS entries (
		id TEXT PRIMARY KEY,
		title TEXT,
		content TEXT,
		lastModifiedBy TEXT,
		lastModifiedAt TEXT
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	app.Get("/entries", func(c *fiber.Ctx) error {
		rows, err := db.Query("SELECT id, title FROM entries")
		if err != nil {
			log.Printf("Failed to query entries: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal Server Error")
		}
		defer rows.Close()

		var entries []Entry
		for rows.Next() {
			var entry Entry
			if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
				log.Printf("Failed to scan entry: %v", err)
				return c.Status(http.StatusInternalServerError).SendString("Internal Server Error")
			}
			entries = append(entries, entry)
		}

		return c.JSON(entries)
	})

	app.Post("/entries", func(c *fiber.Ctx) error {
		var newEntry NewEntry
		if err := c.BodyParser(&newEntry); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Bad Request")
		}

		if len(newEntry.Title) == 0 || len(newEntry.Content) == 0 || len(newEntry.CreatedBy) == 0 {
			return c.Status(http.StatusBadRequest).SendString("Title, Content, and CreatedBy cannot be empty")
		}

		id := uuid.New().String()
		now := time.Now().Format(time.RFC3339)
		_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
			id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, now)
		if err != nil {
			log.Printf("Failed to insert entry: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal Server Error")
		}

		return c.Status(http.StatusCreated).JSON(Entry{
			ID:             id,
			Title:          newEntry.Title,
			Content:        newEntry.Content,
			LastModifiedBy: newEntry.CreatedBy,
			LastModifiedAt: now,
		})
	})

	app.Get("/entries/:entryId", func(c *fiber.Ctx) error {
		entryId := c.Params("entryId")
		var entry Entry
		err := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId).Scan(
			&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).SendString("Entry not found")
		} else if err != nil {
			log.Printf("Failed to query entry: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal Server Error")
		}

		return c.JSON(entry)
	})

	app.Put("/entries/:entryId", func(c *fiber.Ctx) error {
		entryId := c.Params("entryId")
		var updateEntry UpdateEntry
		if err := c.BodyParser(&updateEntry); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Bad Request")
		}

		if len(updateEntry.Content) == 0 || len(updateEntry.ModifiedBy) == 0 {
			return c.Status(http.StatusBadRequest).SendString("Content and ModifiedBy cannot be empty")
		}

		now := time.Now().Format(time.RFC3339)
		res, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
			updateEntry.Content, updateEntry.ModifiedBy, now, entryId)
		if err != nil {
			log.Printf("Failed to update entry: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal Server Error")
		}

		rowsAffected, err := res.RowsAffected()
		if err != nil || rowsAffected == 0 {
			return c.Status(http.StatusNotFound).SendString("Entry not found")
		}

		return c.JSON(Entry{
			ID:             entryId,
			Content:        updateEntry.Content,
			LastModifiedBy: updateEntry.ModifiedBy,
			LastModifiedAt: now,
		})
	})

	app.Get("/entries/:entryId/edits", func(c *fiber.Ctx) error {
		entryId := c.Params("entryId")
		// Placeholder for edit history logic
		return c.SendString(fmt.Sprintf("Edit history for entry %s", entryId))
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}