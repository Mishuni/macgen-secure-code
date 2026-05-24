package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

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
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create messages table if it doesn't exist
	createTableSQL := `CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT NOT NULL,
		username TEXT NOT NULL
	);`
	if _, err := db.Exec(createTableSQL); err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	app.Get("/messages", func(c *fiber.Ctx) error {
		limit := c.Query("limit", "10")
		offset := c.Query("offset", "0")
		sort := c.Query("sort", "DESC")

		rows, err := db.Query(fmt.Sprintf("SELECT content, username FROM messages ORDER BY id %s LIMIT %s OFFSET %s", sort, limit, offset))
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

		_, err := db.Exec("INSERT INTO messages (content, username) VALUES (?, ?)", msg.Content, msg.Username)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error saving message")
		}

		return c.SendStatus(http.StatusOK)
	})

	log.Fatal(app.Listen(":5000"))
}