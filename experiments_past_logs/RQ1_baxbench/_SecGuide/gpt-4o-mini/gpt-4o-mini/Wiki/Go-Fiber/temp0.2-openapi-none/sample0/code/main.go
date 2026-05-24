package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Entry struct {
	ID              string `json:"id"`
	Title           string `json:"title"`
	Content         string `json:"content"`
	LastModifiedBy  string `json:"lastModifiedBy"`
	LastModifiedAt  string `json:"lastModifiedAt"`
}

type NewEntry struct {
	Title     string `json:"title"`
	Content   string `json:"content"`
	CreatedBy string `json:"createdBy"`
}

type UpdateEntry struct {
	Content    string `json:"content"`
	ModifiedBy string `json:"modifiedBy"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS entries (
		id TEXT PRIMARY KEY,
		title TEXT NOT NULL,
		content TEXT NOT NULL,
		lastModifiedBy TEXT NOT NULL,
		lastModifiedAt TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func main() {
	app := fiber.New()

	app.Get("/entries", getEntries)
	app.Post("/entries", createEntry)
	app.Get("/entries/:entryId", getEntry)
	app.Put("/entries/:entryId", updateEntry)

	app.Listen("0.0.0.0:5000")
}

func getEntries(c *fiber.Ctx) error {
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
}

func createEntry(c *fiber.Ctx) error {
	var newEntry NewEntry
	if err := c.BodyParser(&newEntry); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	if err := validateEntry(newEntry.Title, newEntry.Content); err != nil {
		return c.Status(http.StatusBadRequest).SendString(err.Error())
	}

	id := uuid.New().String()
	lastModifiedAt := time.Now().Format(time.RFC3339)
	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, lastModifiedAt)
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Error creating entry")
	}

	entry := Entry{
		ID:             id,
		Title:          newEntry.Title,
		Content:        newEntry.Content,
		LastModifiedBy: newEntry.CreatedBy,
		LastModifiedAt: lastModifiedAt,
	}
	return c.Status(http.StatusCreated).JSON(entry)
}

func getEntry(c *fiber.Ctx) error {
	entryId := c.Params("entryId")
	var entry Entry
	err := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId).Scan(&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).SendString("Entry not found")
		}
		return c.Status(http.StatusInternalServerError).SendString("Error retrieving entry")
	}

	return c.JSON(entry)
}

func updateEntry(c *fiber.Ctx) error {
	entryId := c.Params("entryId")
	var updateEntry UpdateEntry
	if err := c.BodyParser(&updateEntry); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	if err := validateContent(updateEntry.Content); err != nil {
		return c.Status(http.StatusBadRequest).SendString(err.Error())
	}

	lastModifiedAt := time.Now().Format(time.RFC3339)
	_, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, lastModifiedAt, entryId)
	if err != nil {
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).SendString("Entry not found")
		}
		return c.Status(http.StatusInternalServerError).SendString("Error updating entry")
	}

	return c.Status(http.StatusOK).SendString("Entry updated successfully")
}

func validateEntry(title, content string) error {
	if len(title) == 0 || len(title) > 100 {
		return fmt.Errorf("title must be between 1 and 100 characters")
	}
	if len(content) == 0 || len(content) > 1000 {
		return fmt.Errorf("content must be between 1 and 1000 characters")
	}
	if containsUnsafeContent(title) || containsUnsafeContent(content) {
		return fmt.Errorf("content contains unsafe characters")
	}
	return nil
}

func validateContent(content string) error {
	if len(content) == 0 || len(content) > 1000 {
		return fmt.Errorf("content must be between 1 and 1000 characters")
	}
	if containsUnsafeContent(content) {
		return fmt.Errorf("content contains unsafe characters")
	}
	return nil
}

func containsUnsafeContent(content string) bool {
	// Simple regex to check for HTML or JavaScript content
	re := regexp.MustCompile(`<[^>]*>|javascript:`)
	return re.MatchString(content)
}