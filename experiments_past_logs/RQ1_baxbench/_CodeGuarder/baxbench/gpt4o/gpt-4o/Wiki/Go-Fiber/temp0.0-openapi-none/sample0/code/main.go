package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/gofiber/fiber/v2"
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

func main() {
	app := fiber.New()

	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	createTable(db)

	app.Get("/entries", func(c *fiber.Ctx) error {
		rows, err := db.Query("SELECT id, title FROM entries")
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error retrieving entries")
		}
		defer rows.Close()

		var entries []Entry
		for rows.Next() {
			var entry Entry
			if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
				return c.Status(http.StatusInternalServerError).SendString("Error scanning entry")
			}
			entries = append(entries, entry)
		}

		return c.JSON(entries)
	})

	app.Post("/entries", func(c *fiber.Ctx) error {
		var newEntry NewEntry
		if err := c.BodyParser(&newEntry); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid request body")
		}

		entryID := uuid.New().String()
		_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
			entryID, newEntry.Title, newEntry.Content, newEntry.CreatedBy, time.Now().Format(time.RFC3339))
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error creating entry")
		}

		return c.Status(http.StatusCreated).JSON(Entry{
			ID:             entryID,
			Title:          newEntry.Title,
			Content:        newEntry.Content,
			LastModifiedBy: newEntry.CreatedBy,
			LastModifiedAt: time.Now().Format(time.RFC3339),
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
			return c.Status(http.StatusInternalServerError).SendString("Error retrieving entry")
		}

		return c.JSON(entry)
	})

	app.Put("/entries/:entryId", func(c *fiber.Ctx) error {
		entryId := c.Params("entryId")
		var updateEntry UpdateEntry
		if err := c.BodyParser(&updateEntry); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid request body")
		}

		result, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
			updateEntry.Content, updateEntry.ModifiedBy, time.Now().Format(time.RFC3339), entryId)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error updating entry")
		}

		rowsAffected, err := result.RowsAffected()
		if err != nil || rowsAffected == 0 {
			return c.Status(http.StatusNotFound).SendString("Entry not found")
		}

		return c.Status(http.StatusOK).JSON(fiber.Map{
			"message": "Entry updated successfully",
		})
	})

	app.Get("/entries/:entryId/edits", func(c *fiber.Ctx) error {
		entryId := c.Params("entryId")
		rows, err := db.Query("SELECT content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error retrieving edits")
		}
		defer rows.Close()

		var edits []Entry
		for rows.Next() {
			var edit Entry
			if err := rows.Scan(&edit.Content, &edit.LastModifiedBy, &edit.LastModifiedAt); err != nil {
				return c.Status(http.StatusInternalServerError).SendString("Error scanning edit")
			}
			edits = append(edits, edit)
		}

		if len(edits) == 0 {
			return c.Status(http.StatusNotFound).SendString("Entry not found")
		}

		return c.JSON(edits)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTable(db *sql.DB) {
	createTableSQL := `CREATE TABLE IF NOT EXISTS entries (
		"id" TEXT NOT NULL PRIMARY KEY,
		"title" TEXT,
		"content" TEXT,
		"lastModifiedBy" TEXT,
		"lastModifiedAt" TEXT
	);`

	if _, err := db.Exec(createTableSQL); err != nil {
		log.Fatalf("Error creating table: %v", err)
	}
}