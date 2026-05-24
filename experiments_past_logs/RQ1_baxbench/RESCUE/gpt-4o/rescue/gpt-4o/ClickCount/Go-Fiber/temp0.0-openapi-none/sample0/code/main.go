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

func main() {
	// Initialize Fiber app
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create table if it doesn't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS clicks (
			id TEXT PRIMARY KEY,
			timestamp TEXT NOT NULL
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// POST /click - Register a click
	app.Post("/click", func(c *fiber.Ctx) error {
		// Generate a new UUID for the click
		id := uuid.New().String()
		timestamp := time.Now().UTC().Format(time.RFC3339)

		// Insert the click into the database using a parameterized query
		_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", id, timestamp)
		if err != nil {
			log.Printf("Failed to insert click: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to register click")
		}

		return c.Status(fiber.StatusCreated).SendString("Click registered successfully")
	})

	// GET /clicks - Retrieve clicks
	app.Get("/clicks", func(c *fiber.Ctx) error {
		// Get query parameters
		date := c.Query("date")
		direction := c.Query("direction")

		// Validate query parameters
		if date == "" || direction == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Missing required query parameters")
		}
		if direction != "<" && direction != ">" && direction != "<=" && direction != ">=" {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid direction parameter")
		}

		// Query the database using a parameterized query
		query := "SELECT id, timestamp FROM clicks WHERE timestamp " + direction + " ?"
		rows, err := db.Query(query, date)
		if err != nil {
			log.Printf("Failed to query clicks: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to retrieve clicks")
		}
		defer rows.Close()

		// Parse the results
		var clicks []map[string]string
		for rows.Next() {
			var id, timestamp string
			if err := rows.Scan(&id, &timestamp); err != nil {
				log.Printf("Failed to scan row: %v", err)
				return c.Status(fiber.StatusInternalServerError).SendString("Failed to retrieve clicks")
			}
			clicks = append(clicks, map[string]string{
				"id":        id,
				"timestamp": timestamp,
			})
		}

		// Check if no clicks were found
		if len(clicks) == 0 {
			return c.Status(fiber.StatusNotFound).SendString("No clicks found")
		}

		// Return the results as JSON
		return c.JSON(clicks)
	})

	// Start the server
	log.Println("Server is running on http://0.0.0.0:5000")
	if err := app.Listen("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}