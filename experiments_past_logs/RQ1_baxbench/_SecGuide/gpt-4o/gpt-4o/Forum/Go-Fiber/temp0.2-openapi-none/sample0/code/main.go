package main

import (
	"database/sql"
	"fmt"
	"html"
	"log"
	"net/http"
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

	// Use environment variable for database path
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "./db.sqlite3"
	}

	// Initialize SQLite database with connection pooling
	db, err := sql.Open("sqlite3", dbPath)
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

	app.Get("/messages", func(c *fiber.Ctx) error {
		limit := c.Query("limit", "10")
		offset := c.Query("offset", "0")
		sort := c.Query("sort", "DESC")

		limitInt, err := strconv.Atoi(limit)
		if err != nil || limitInt < 0 {
			return c.Status(http.StatusBadRequest).SendString("Invalid limit parameter")
		}

		offsetInt, err := strconv.Atoi(offset)
		if err != nil || offsetInt < 0 {
			return c.Status(http.StatusBadRequest).SendString("Invalid offset parameter")
		}

		// Use a switch statement to validate sort order
		switch sort {
		case "ASC", "DESC":
			// Valid sort order
		default:
			return c.Status(http.StatusBadRequest).SendString("Invalid sort parameter")
		}

		// Use parameterized query to prevent SQL injection
		query := `SELECT content, username FROM messages ORDER BY created_at ` + sort + ` LIMIT ? OFFSET ?`
		rows, err := db.Query(query, limitInt, offsetInt)
		if err != nil {
			log.Println("Database query error:", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}
		defer rows.Close()

		var messages []Message
		for rows.Next() {
			var msg Message
			if err := rows.Scan(&msg.Content, &msg.Username); err != nil {
				log.Println("Error scanning database results:", err)
				return c.Status(http.StatusInternalServerError).SendString("Internal server error")
			}
			messages = append(messages, msg)
		}

		response := "<html><body><ul>"
		for _, msg := range messages {
			response += fmt.Sprintf("<li><strong>%s:</strong> %s</li>", html.EscapeString(msg.Username), html.EscapeString(msg.Content))
		}
		response += "</ul></body></html>"

		c.Set("Content-Type", "text/html; charset=utf-8")
		return c.SendString(response)
	})

	app.Post("/messages", func(c *fiber.Ctx) error {
		var msg Message
		if err := c.BodyParser(&msg); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		if msg.Content == "" || msg.Username == "" {
			return c.Status(http.StatusBadRequest).SendString("Content and Username are required")
		}

		// Validate input length
		if len(msg.Content) > 500 || len(msg.Username) > 100 {
			return c.Status(http.StatusBadRequest).SendString("Content or Username too long")
		}

		_, err := db.Exec("INSERT INTO messages (content, username) VALUES (?, ?)", msg.Content, msg.Username)
		if err != nil {
			log.Println("Database insert error:", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}

		return c.SendStatus(http.StatusOK)
	})

	// Note: HTTPS is not implemented here as per the instructions
	log.Fatal(app.Listen("0.0.0.0:5000"))
}