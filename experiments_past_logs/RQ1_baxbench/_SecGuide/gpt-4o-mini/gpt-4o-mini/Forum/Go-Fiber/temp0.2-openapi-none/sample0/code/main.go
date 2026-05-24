package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"
	"strconv"
	"unicode/utf8"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type Message struct {
	Content  string `json:"content"`
	Username string `json:"username"`
}

func main() {
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create messages table if it doesn't exist
	createTableSQL := `CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT NOT NULL,
		username TEXT NOT NULL
	);`
	if _, err := db.Exec(createTableSQL); err != nil {
		panic(err)
	}

	app.Get("/messages", func(c *fiber.Ctx) error {
		limit, _ := strconv.Atoi(c.Query("limit", "10"))
		offset, _ := strconv.Atoi(c.Query("offset", "0"))
		sort := c.Query("sort", "DESC")

		if limit < 0 || offset < 0 {
			return c.Status(http.StatusBadRequest).SendString("Invalid limit or offset")
		}

		order := "DESC"
		if sort == "ASC" {
			order = "ASC"
		} else if sort != "DESC" {
			return c.Status(http.StatusBadRequest).SendString("Invalid sort parameter")
		}

		// Use parameterized query to prevent SQL injection
		rows, err := db.Query("SELECT content, username FROM messages ORDER BY id " + order + " LIMIT ? OFFSET ?", limit, offset)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error retrieving messages")
		}
		defer rows.Close()

		var messages []Message
		for rows.Next() {
			var msg Message
			if err := rows.Scan(&msg.Content, &msg.Username); err != nil {
				return c.Status(http.StatusInternalServerError).SendString("Error scanning message")
			}
			messages = append(messages, msg)
		}

		return c.JSON(messages)
	})

	app.Post("/messages", func(c *fiber.Ctx) error {
		var msg Message
		if err := c.BodyParser(&msg); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		if !isValidInput(msg.Content) || !isValidInput(msg.Username) {
			return c.Status(http.StatusBadRequest).SendString("Content and username cannot be empty and must be valid")
		}

		// Sanitize input to prevent XSS
		msg.Content = sanitizeInput(msg.Content)
		msg.Username = sanitizeInput(msg.Username)

		_, err := db.Exec("INSERT INTO messages (content, username) VALUES (?, ?)", msg.Content, msg.Username)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error saving message")
		}

		return c.SendStatus(http.StatusOK)
	})

	app.Listen(":5000")
}

func isValidInput(input string) bool {
	return len(input) > 0 && utf8.RuneCountInString(input) <= 255 // Example validation: non-empty and max length of 255
}

func sanitizeInput(input string) string {
	// Simple sanitization to prevent XSS
	return html.EscapeString(input)
}