package main

import (
	"database/sql"
	"log"
	"os"
	"strconv"

	"github.com/gofiber/fiber/v2"
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

	// Create messages table if it doesn't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS messages (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL,
			content TEXT NOT NULL,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Route to get all messages
	app.Get("/messages", func(c *fiber.Ctx) error {
		// Parse query parameters
		limit := c.Query("limit", "10")
		offset := c.Query("offset", "0")
		sort := c.Query("sort", "DESC")

		// Validate sort parameter
		if sort != "ASC" && sort != "DESC" {
			sort = "DESC"
		}

		// Convert limit and offset to integers
		limitInt, err := strconv.Atoi(limit)
		if err != nil || limitInt < 1 {
			limitInt = 10
		}
		offsetInt, err := strconv.Atoi(offset)
		if err != nil || offsetInt < 0 {
			offsetInt = 0
		}

		// Query messages from the database
		query := `
			SELECT username, content, created_at
			FROM messages
			ORDER BY created_at ` + sort + `
			LIMIT ? OFFSET ?
		`
		rows, err := db.Query(query, limitInt, offsetInt)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to fetch messages")
		}
		defer rows.Close()

		// Build response
		messages := []map[string]interface{}{}
		for rows.Next() {
			var username, content, createdAt string
			if err := rows.Scan(&username, &content, &createdAt); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Failed to parse messages")
			}
			messages = append(messages, map[string]interface{}{
				"username":   username,
				"content":    content,
				"created_at": createdAt,
			})
		}

		return c.JSON(messages)
	})

	// Route to post a new message
	app.Post("/messages", func(c *fiber.Ctx) error {
		// Parse request body
		type Message struct {
			Username string `json:"username"`
			Content  string `json:"content"`
		}
		var msg Message
		if err := c.BodyParser(&msg); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		// Validate input
		if msg.Username == "" || msg.Content == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Username and content are required")
		}

		// Insert message into the database
		_, err := db.Exec(`
			INSERT INTO messages (username, content)
			VALUES (?, ?)
		`, msg.Username, msg.Content)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to save message")
		}

		return c.SendString("Message posted successfully")
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}