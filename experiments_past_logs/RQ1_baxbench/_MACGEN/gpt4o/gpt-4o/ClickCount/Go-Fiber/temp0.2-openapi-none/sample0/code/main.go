package main

import (
	"database/sql"
	"log"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Click struct {
	ID        string    `json:"id"`
	Timestamp time.Time `json:"timestamp"`
}

func main() {
	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create clicks table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME NOT NULL
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Initialize Fiber app
	app := fiber.New()

	// Register a click
	app.Post("/click", func(c *fiber.Ctx) error {
		id := uuid.New().String()
		timestamp := time.Now()

		_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", id, timestamp)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		return c.Status(fiber.StatusCreated).SendString("Click registered successfully")
	})

	// Retrieve clicks
	app.Get("/clicks", func(c *fiber.Ctx) error {
		date := c.Query("date")
		direction := c.Query("direction")

		if date == "" || direction == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		// Validate direction
		validDirections := map[string]bool{"<": true, ">": true, "<=": true, ">=": true}
		if !validDirections[direction] {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid direction")
		}

		// Validate date format
		_, err := time.Parse("2006-01-02", date)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid date format")
		}

		query := "SELECT id, timestamp FROM clicks WHERE timestamp " + direction + " ?"
		rows, err := db.Query(query, date)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}
		defer rows.Close()

		var clicks []Click
		for rows.Next() {
			var click Click
			if err := rows.Scan(&click.ID, &click.Timestamp); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Error retrieving clicks")
			}
			clicks = append(clicks, click)
		}

		if len(clicks) == 0 {
			return c.Status(fiber.StatusNotFound).SendString("No clicks found")
		}

		return c.JSON(clicks)
	})

	// Start server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}