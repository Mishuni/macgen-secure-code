package main

import (
	"database/sql"
	"log"
	"strconv"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize the Fiber app
	app := fiber.New()

	// Connect to SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create messages table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT NOT NULL,
		content TEXT NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Route to get all messages
	app.Get("/messages", func(c *fiber.Ctx) error {
		limit := c.Query("limit", "10")
		offset := c.Query("offset", "0")
		sort := c.Query("sort", "desc")

		limitInt, err := strconv.Atoi(limit)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid limit")
		}

		offsetInt, err := strconv.Atoi(offset)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid offset")
		}

		if sort != "ASC" && sort != "DESC" && sort != "asc" && sort != "desc" {
			sort = "desc"
		}

		query := `SELECT username, content, created_at FROM messages ORDER BY created_at ` + sort + ` LIMIT ? OFFSET ?`
		rows, err := db.Query(query, limitInt, offsetInt)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database query error")
		}
		defer rows.Close()

		var messages []map[string]string
		for rows.Next() {
			var username, content, createdAt string
			if err := rows.Scan(&username, &content, &createdAt); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Error scanning row")
			}
			messages = append(messages, map[string]string{
				"username":  username,
				"content":   content,
				"createdAt": createdAt,
			})
		}

		return c.JSON(messages)
	})

	// Route to post a new message
	app.Post("/messages", func(c *fiber.Ctx) error {
		type Message struct {
			Username string `json:"username"`
			Content  string `json:"content"`
		}

		var msg Message
		if err := c.BodyParser(&msg); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		if msg.Username == "" || msg.Content == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Username and content are required")
		}

		stmt, err := db.Prepare("INSERT INTO messages (username, content) VALUES (?, ?)")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database preparation error")
		}
		defer stmt.Close()

		_, err = stmt.Exec(msg.Username, msg.Content)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database insert error")
		}

		return c.SendStatus(fiber.StatusOK)
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}