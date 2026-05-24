package main

import (
	"database/sql"
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
	Title    string `json:"title"`
	Content  string `json:"content"`
	CreatedBy string `json:"createdBy"`
}

type UpdateEntry struct {
	Content   string `json:"content"`
	ModifiedBy string `json:"modifiedBy"`
	Summary   string `json:"summary"`
}

type Edit struct {
	Content       string `json:"content"`
	LastModifiedBy string `json:"lastModifiedBy"`
	LastModifiedAt string `json:"lastModifiedAt"`
	Summary       string `json:"summary"`
}

func main() {
	app := fiber.New()

	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	createTables(db)

	app.Get("/entries", func(c *fiber.Ctx) error {
		rows, err := db.Query("SELECT id, title FROM entries")
		if err != nil {
			return err
		}
		defer rows.Close()

		var entries []Entry
		for rows.Next() {
			var entry Entry
			if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
				return err
			}
			entries = append(entries, entry)
		}

		return c.JSON(entries)
	})

	app.Post("/entries", func(c *fiber.Ctx) error {
		var newEntry NewEntry
		if err := c.BodyParser(&newEntry); err != nil {
			return err
		}

		id := uuid.New().String()
		now := time.Now().Format(time.RFC3339)

		_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
			id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, now)
		if err != nil {
			return err
		}

		_, err = db.Exec("INSERT INTO edits (entryId, content, lastModifiedBy, lastModifiedAt, summary) VALUES (?, ?, ?, ?, ?)",
			id, newEntry.Content, newEntry.CreatedBy, now, "Initial creation")
		if err != nil {
			return err
		}

		entry := Entry{
			ID:            id,
			Title:         newEntry.Title,
			Content:       newEntry.Content,
			LastModifiedBy: newEntry.CreatedBy,
			LastModifiedAt: now,
		}

		return c.Status(fiber.StatusCreated).JSON(entry)
	})

	app.Get("/entries/:entryId", func(c *fiber.Ctx) error {
		entryId := c.Params("entryId")

		var entry Entry
		err := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId).
			Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)
		if err == sql.ErrNoRows {
			return c.Status(fiber.StatusNotFound).SendString("Entry not found")
		} else if err != nil {
			return err
		}

		return c.JSON(entry)
	})

	app.Put("/entries/:entryId", func(c *fiber.Ctx) error {
		entryId := c.Params("entryId")

		var updateEntry UpdateEntry
		if err := c.BodyParser(&updateEntry); err != nil {
			return err
		}

		now := time.Now().Format(time.RFC3339)

		result, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
			updateEntry.Content, updateEntry.ModifiedBy, now, entryId)
		if err != nil {
			return err
		}

		rowsAffected, err := result.RowsAffected()
		if err != nil {
			return err
		}

		if rowsAffected == 0 {
			return c.Status(fiber.StatusNotFound).SendString("Entry not found")
		}

		_, err = db.Exec("INSERT INTO edits (entryId, content, lastModifiedBy, lastModifiedAt, summary) VALUES (?, ?, ?, ?, ?)",
			entryId, updateEntry.Content, updateEntry.ModifiedBy, now, updateEntry.Summary)
		if err != nil {
			return err
		}

		var entry Entry
		err = db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId).
			Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)
		if err != nil {
			return err
		}

		return c.JSON(entry)
	})

	app.Get("/entries/:entryId/edits", func(c *fiber.Ctx) error {
		entryId := c.Params("entryId")

		rows, err := db.Query("SELECT content, lastModifiedBy, lastModifiedAt, summary FROM edits WHERE entryId = ?", entryId)
		if err != nil {
			return err
		}
		defer rows.Close()

		var edits []Edit
		for rows.Next() {
			var edit Edit
			if err := rows.Scan(&edit.Content, &edit.LastModifiedBy, &edit.LastModifiedAt, &edit.Summary); err != nil {
				return err
			}
			edits = append(edits, edit)
		}

		if len(edits) == 0 {
			return c.Status(fiber.StatusNotFound).SendString("Entry not found")
		}

		return c.JSON(edits)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	createEntriesTableSQL := `CREATE TABLE IF NOT EXISTS entries (
		"id" TEXT NOT NULL PRIMARY KEY,
		"title" TEXT,
		"content" TEXT,
		"lastModifiedBy" TEXT,
		"lastModifiedAt" TEXT
	);`

	createEditsTableSQL := `CREATE TABLE IF NOT EXISTS edits (
		"entryId" TEXT,
		"content" TEXT,
		"lastModifiedBy" TEXT,
		"lastModifiedAt" TEXT,
		"summary" TEXT,
		FOREIGN KEY(entryId) REFERENCES entries(id)
	);`

	statement, err := db.Prepare(createEntriesTableSQL)
	if err != nil {
		log.Fatal(err)
	}
	statement.Exec()

	statement, err = db.Prepare(createEditsTableSQL)
	if err != nil {
		log.Fatal(err)
	}
	statement.Exec()
}