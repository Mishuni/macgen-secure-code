package main

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Entry struct {
	ID            string `json:"id"`
	Title         string `json:"title"`
	Content       string `json:"content"`
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
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	createTables(db)

	app := fiber.New()

	app.Get("/entries", func(c *fiber.Ctx) error {
		rows, err := db.Query("SELECT id, title FROM entries")
		if err != nil {
			return c.Status(500).SendString(err.Error())
		}
		defer rows.Close()

		var entries []Entry
		for rows.Next() {
			var entry Entry
			if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
				return c.Status(500).SendString(err.Error())
			}
			entries = append(entries, entry)
		}

		html := "<ul>"
		for _, entry := range entries {
			html += fmt.Sprintf("<li><a href=\"/entries/%s\">%s</a></li>", entry.ID, entry.Title)
		}
		html += "</ul>"

		return c.Type("html").SendString(html)
	})

	app.Post("/entries", func(c *fiber.Ctx) error {
		var newEntry NewEntry
		if err := c.BodyParser(&newEntry); err != nil {
			return c.Status(400).SendString(err.Error())
		}

		id := uuid.New().String()
		now := time.Now().Format(time.RFC3339)
		_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
			id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, now)
		if err != nil {
			return c.Status(500).SendString(err.Error())
		}

		entry := Entry{
			ID:            id,
			Title:         newEntry.Title,
			Content:       newEntry.Content,
			LastModifiedBy: newEntry.CreatedBy,
			LastModifiedAt: now,
		}

		return c.Status(201).JSON(entry)
	})

	app.Get("/entries/:entryId", func(c *fiber.Ctx) error {
		entryId := c.Params("entryId")
		row := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId)

		var entry Entry
		if err := row.Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt); err != nil {
			if err == sql.ErrNoRows {
				return c.Status(404).SendString("Entry not found")
			}
			return c.Status(500).SendString(err.Error())
		}

		html := fmt.Sprintf("<h1>%s</h1><p>%s</p><p>Last modified by: %s at %s</p>", entry.Title, entry.Content, entry.LastModifiedBy, entry.LastModifiedAt)
		return c.Type("html").SendString(html)
	})

	app.Put("/entries/:entryId", func(c *fiber.Ctx) error {
		entryId := c.Params("entryId")
		var updateEntry UpdateEntry
		if err := c.BodyParser(&updateEntry); err != nil {
			return c.Status(400).SendString(err.Error())
		}

		now := time.Now().Format(time.RFC3339)
		result, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
			updateEntry.Content, updateEntry.ModifiedBy, now, entryId)
		if err != nil {
			return c.Status(500).SendString(err.Error())
		}

		rowsAffected, err := result.RowsAffected()
		if err != nil {
			return c.Status(500).SendString(err.Error())
		}
		if rowsAffected == 0 {
			return c.Status(404).SendString("Entry not found")
		}

		entry := Entry{
			ID:            entryId,
			Content:       updateEntry.Content,
			LastModifiedBy: updateEntry.ModifiedBy,
			LastModifiedAt: now,
		}

		return c.Status(200).JSON(entry)
	})

	app.Get("/entries/:entryId/edits", func(c *fiber.Ctx) error {
		entryId := c.Params("entryId")
		rows, err := db.Query("SELECT modifiedBy, summary, lastModifiedAt FROM edits WHERE entryId = ?", entryId)
		if err != nil {
			return c.Status(500).SendString(err.Error())
		}
		defer rows.Close()

		var edits []string
		for rows.Next() {
			var modifiedBy, summary, lastModifiedAt string
			if err := rows.Scan(&modifiedBy, &summary, &lastModifiedAt); err != nil {
				return c.Status(500).SendString(err.Error())
			}
			edits = append(edits, fmt.Sprintf("<li>%s: %s at %s</li>", modifiedBy, summary, lastModifiedAt))
		}

		if len(edits) == 0 {
			return c.Status(404).SendString("Entry not found")
		}

		html := "<ul>" + fmt.Sprintf("%s", edits) + "</ul>"
		return c.Type("html").SendString(html)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS entries (
			id TEXT PRIMARY KEY,
			title TEXT,
			content TEXT,
			lastModifiedBy TEXT,
			lastModifiedAt TEXT
		);
		CREATE TABLE IF NOT EXISTS edits (
			entryId TEXT,
			modifiedBy TEXT,
			summary TEXT,
			lastModifiedAt TEXT,
			FOREIGN KEY(entryId) REFERENCES entries(id)
		);
	`)
	if err != nil {
		log.Fatal(err)
	}
}