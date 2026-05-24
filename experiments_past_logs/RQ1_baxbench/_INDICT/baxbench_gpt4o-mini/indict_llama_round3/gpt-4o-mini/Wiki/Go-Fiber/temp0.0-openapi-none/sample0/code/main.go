package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
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

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
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
		fmt.Println(err)
		os.Exit(1)
	}
}

func main() {
	app := fiber.New()

	app.Get("/entries", getEntries)
	app.Post("/entries", createEntry)
	app.Get("/entries/:entryId", getEntry)
	app.Put("/entries/:entryId", updateEntry)
	app.Get("/entries/:entryId/edits", getEntryEdits)

	app.Listen(":5000")
}

func getEntries(c *fiber.Ctx) error {
	rows, err := db.Query("SELECT id, title FROM entries")
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString(err.Error())
	}
	defer rows.Close()

	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.Scan(&entry.ID, &entry.Title); err != nil {
			return c.Status(http.StatusInternalServerError).SendString(err.Error())
		}
		entries = append(entries, entry)
	}

	response := make([]map[string]string, len(entries))
	for i, entry := range entries {
		response[i] = map[string]string{
			"title": entry.Title,
			"link":  fmt.Sprintf("/entries/%s", entry.ID),
		}
	}

	return c.JSON(response)
}

func createEntry(c *fiber.Ctx) error {
	var newEntry NewEntry
	if err := c.BodyParser(&newEntry); err != nil {
		return c.Status(http.StatusBadRequest).SendString(err.Error())
	}

	id := uuid.New().String()
	lastModifiedAt := time.Now().Format(time.RFC3339)

	_, err := db.Exec("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)",
		id, newEntry.Title, newEntry.Content, newEntry.CreatedBy, lastModifiedAt)
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString(err.Error())
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

	err := db.QueryRow("SELECT id, title, content, lastModifiedBy, lastModifiedAt FROM entries WHERE id = ?", entryId).Scan(
		&entry.ID, &entry.Title, &entry.Content, &entry.LastModifiedBy, &entry.LastModifiedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).SendString("Entry not found")
		}
		return c.Status(http.StatusInternalServerError).SendString(err.Error())
	}

	return c.JSON(entry)
}

func updateEntry(c *fiber.Ctx) error {
	entryId := c.Params("entryId")
	var updateEntry UpdateEntry
	if err := c.BodyParser(&updateEntry); err != nil {
		return c.Status(http.StatusBadRequest).SendString(err.Error())
	}

	lastModifiedAt := time.Now().Format(time.RFC3339)

	result, err := db.Exec("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?",
		updateEntry.Content, updateEntry.ModifiedBy, lastModifiedAt, entryId)
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString(err.Error())
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString(err.Error())
	}
	if rowsAffected == 0 {
		return c.Status(http.StatusNotFound).SendString("Entry not found")
	}

	return c.Status(http.StatusOK).SendString("Entry updated successfully")
}

func getEntryEdits(c *fiber.Ctx) error {
	return c.Status(http.StatusNotImplemented).SendString("Edit history functionality not implemented")
}