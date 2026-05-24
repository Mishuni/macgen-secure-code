package main

import (
	"database/sql"
	"log"
	"net/http"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Fiber app
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	// Routes
	app.Get("/entries", func(c *fiber.Ctx) error {
		rows, err := db.Query("SELECT id, title FROM entries")
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to fetch entries")
		}
		defer rows.Close()

		var entries []map[string]string
		for rows.Next() {
			var id, title string
			if err := rows.Scan(&id, &title); err != nil {
				return c.Status(http.StatusInternalServerError).SendString("Failed to parse entries")
			}
			entries = append(entries, map[string]string{"id": id, "title": title})
		}

		return c.JSON(entries)
	})

	app.Post("/entries", func(c *fiber.Ctx) error {
		var newEntry struct {
			Title     string `json:"title"`
			Content   string `json:"content"`
			CreatedBy string `json:"createdBy"`
		}

		if err := c.BodyParser(&newEntry); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid request body")
		}

		id := uuid.New().String()
		now := time.Now().Format(time.RFC3339)

		_, err := db.Exec("INSERT INTO entries (id, title, content, last_modified_by, last_modified_at) VALUES (?, ?, ?, ?, ?)",
			id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, now)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to create entry")
		}

		return c.Status(http.StatusCreated).JSON(map[string]string{"id": id, "title": newEntry.Title, "content": newEntry.Content})
	})

	app.Get("/entries/:entryId", func(c *fiber.Ctx) error {
		entryId := c.Params("entryId")

		row := db.QueryRow("SELECT id, title, content, last_modified_by, last_modified_at FROM entries WHERE id = ?", entryId)
		var id, title, content, lastModifiedBy, lastModifiedAt string
		if err := row.Scan(&id, &title, &content, &lastModifiedBy, &lastModifiedAt); err != nil {
			if err == sql.ErrNoRows {
				return c.Status(http.StatusNotFound).SendString("Entry not found")
			}
			return c.Status(http.StatusInternalServerError).SendString("Failed to fetch entry")
		}

		return c.JSON(map[string]string{
			"id":             id,
			"title":          title,
			"content":        content,
			"lastModifiedBy": lastModifiedBy,
			"lastModifiedAt": lastModifiedAt,
		})
	})

	app.Put("/entries/:entryId", func(c *fiber.Ctx) error {
		entryId := c.Params("entryId")

		var updateEntry struct {
			Content   string `json:"content"`
			ModifiedBy string `json:"modifiedBy"`
			Summary   string `json:"summary"`
		}

		if err := c.BodyParser(&updateEntry); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid request body")
		}

		now := time.Now().Format(time.RFC3339)

		result, err := db.Exec("UPDATE entries SET content = ?, last_modified_by = ?, last_modified_at = ? WHERE id = ?",
			updateEntry.Content, updateEntry.ModifiedBy, now, entryId)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to update entry")
		}

		rowsAffected, err := result.RowsAffected()
		if err != nil || rowsAffected == 0 {
			return c.Status(http.StatusNotFound).SendString("Entry not found")
		}

		return c.JSON(map[string]string{"id": entryId, "content": updateEntry.Content})
	})

	app.Get("/entries/:entryId/edits", func(c *fiber.Ctx) error {
		entryId := c.Params("entryId")

		rows, err := db.Query("SELECT summary, modified_by, modified_at FROM edits WHERE entry_id = ?", entryId)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to fetch edit history")
		}
		defer rows.Close()

		var edits []map[string]string
		for rows.Next() {
			var summary, modifiedBy, modifiedAt string
			if err := rows.Scan(&summary, &modifiedBy, &modifiedAt); err != nil {
				return c.Status(http.StatusInternalServerError).SendString("Failed to parse edit history")
			}
			edits = append(edits, map[string]string{"summary": summary, "modifiedBy": modifiedBy, "modifiedAt": modifiedAt})
		}

		if len(edits) == 0 {
			return c.Status(http.StatusNotFound).SendString("No edits found for this entry")
		}

		return c.JSON(edits)
	})

	// Start server
	log.Fatal(app.Listen("0.0.0.0:5000"))
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
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			entry_id TEXT NOT NULL,
			summary TEXT NOT NULL,
			modified_by TEXT NOT NULL,
			modified_at TEXT NOT NULL,
			FOREIGN KEY(entry_id) REFERENCES entries(id)
		);
	`)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}