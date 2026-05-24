package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"strconv"

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
		log.Fatal(err)
	}
	defer db.Close()

	// Create messages table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT NOT NULL,
		username TEXT NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// GET /messages endpoint
	app.Get("/messages", func(c *fiber.Ctx) error {
		limit := c.Query("limit", "10")
		offset := c.Query("offset", "0")
		sort := c.Query("sort", "DESC")

		// Validate query parameters
		limitInt, err := strconv.Atoi(limit)
		if err != nil || limitInt < 0 {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid limit parameter")
		}

		offsetInt, err := strconv.Atoi(offset)
		if err != nil || offsetInt < 0 {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid offset parameter")
		}

		if sort != "ASC" && sort != "DESC" {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid sort parameter")
		}

		rows, err := db.Query(fmt.Sprintf("SELECT content, username FROM messages ORDER BY created_at %s LIMIT ? OFFSET ?", sort), limitInt, offsetInt)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database query error")
		}
		defer rows.Close()

		var messages []Message
		for rows.Next() {
			var msg Message
			if err := rows.Scan(&msg.Content, &msg.Username); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Error scanning row")
			}
			messages = append(messages, msg)
		}

		return c.JSON(messages)
	})

	// POST /messages endpoint
	app.Post("/messages", func(c *fiber.Ctx) error {
		var msg Message
		if err := c.BodyParser(&msg); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		if msg.Content == "" || msg.Username == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Content and Username are required")
		}

		_, err := db.Exec("INSERT INTO messages (content, username) VALUES (?, ?)", msg.Content, msg.Username)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Database insert error")
		}

		return c.SendStatus(fiber.StatusOK)
	})

	// Start server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}