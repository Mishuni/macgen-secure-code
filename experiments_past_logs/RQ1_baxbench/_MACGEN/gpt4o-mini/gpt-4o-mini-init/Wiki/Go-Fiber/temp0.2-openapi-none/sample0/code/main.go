package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"regexp"
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
	Content    string `json:"content"`
	ModifiedBy string `json:"modifiedBy"`
	Summary    string `json:"summary"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
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
		log.Fatal(err)
	}

	defer db.Close()
}

func main() {
	app := fiber.New()

	app.Get("/entries", getEntries)
	app.Post("/entries", createEntry)
	app.Get("/entries/:entryId", getEntry)
	app.Put("/entries/:entryId", updateEntry)
	app.Get("/entries/:entryId/edits", getEntryEdits)

	log.Fatal(app.Listen(":5000"))
}

func getEntries(c *fiber.Ctx) error {
	rows, err := db.Query("SELECT id, title FROM entries")
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Database error")
	}
	defer rows.Close()

	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Database error")
		}
		entries = append(entries, entry)
	}

	return c.Render("entries.html", fiber.Map{"entries": entries})
}

func createEntry(c *fiber.Ctx) error {
	var newEntry NewEntry
	if err := c.BodyParser(&newEntry); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	newEntry.Title = sanitize(newEntry.Title)
	newEntry.Content = sanitize(newEntry.Content)

	id := uuid.New().String()
	lastModifiedAt := time.Now().Format(time.RFC3339)
	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, lastModifiedAt)
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Database error")
	}

	entry := Entry{ID: id, Title: newEntry.Title, Content: newEntry.Content, LastModifiedBy: newEntry.CreatedBy, LastModifiedAt: lastModifiedAt}
	return c.Status(http.StatusCreated).JSON(entry)
}

func getEntry(c *fiber.Ctx) error {
	entryId := c.Params("entryId")
	if _, err := uuid.Parse(entryId); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid entry ID")
	}

	row := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId)

	var entry Entry
	if err := row.Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt); err != nil {
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).SendString("Entry not found")
		}
		return c.Status(http.StatusInternalServerError).SendString("Database error")
	}

	return c.Render("entry.html", entry)
}

func updateEntry(c *fiber.Ctx) error {
	entryId := c.Params("entryId")
	if _, err := uuid.Parse(entryId); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid entry ID")
	}

	var updateEntry UpdateEntry
	if err := c.BodyParser(&updateEntry); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	updateEntry.Content = sanitize(updateEntry.Content)
	lastModifiedAt := time.Now().Format(time.RFC3339)
	_, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, lastModifiedAt, entryId)
	if err != nil {
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).SendString("Entry not found")
		}
		return c.Status(http.StatusInternalServerError).SendString("Database error")
	}

	entry := Entry{ID: entryId, Content: updateEntry.Content, LastModifiedBy: updateEntry.ModifiedBy, LastModifiedAt: lastModifiedAt}
	return c.JSON(entry)
}

func getEntryEdits(c *fiber.Ctx) error {
	entryId := c.Params("entryId")
	if _, err := uuid.Parse(entryId); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid entry ID")
	}
	// Placeholder for edit history retrieval
	return c.Status(http.StatusNotImplemented).SendString("Edit history not implemented")
}

func sanitize(input string) string {
	re := regexp.MustCompile(`[<>]`)
	return re.ReplaceAllString(input, "")
}