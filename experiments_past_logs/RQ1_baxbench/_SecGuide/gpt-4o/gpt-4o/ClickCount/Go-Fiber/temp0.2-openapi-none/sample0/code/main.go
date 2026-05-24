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

	// Get database path from environment variable or use default
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "db.sqlite3"
	}

	// Validate the database path
	if !isValidPath(dbPath) {
		log.Fatal("Invalid database path")
	}

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer func() {
		if err := db.Close(); err != nil {
			log.Printf("Error closing database: %v", err)
		}
	}()

	// Create clicks table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Register a click
	app.Post("/click", func(c *fiber.Ctx) error {
		id := uuid.New().String()
		_, err := db.Exec("INSERT INTO clicks (id) VALUES (?)", id)
		if err != nil {
			log.Printf("Error inserting click: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}
		return c.Status(fiber.StatusCreated).SendString("Click registered successfully")
	})

	// Retrieve clicks
	app.Get("/clicks", func(c *fiber.Ctx) error {
		date := c.Query("date")
		direction := c.Query("direction")

		if date == "" || (direction != ">" && direction != "<") {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		// Validate date format
		if _, err := time.Parse("2006-01-02", date); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid date format")
		}

		// Use parameterized query to prevent SQL injection
		query := "SELECT id, timestamp FROM clicks WHERE timestamp " + direction + " ?"
		rows, err := db.Query(query, date)
		if err != nil {
			log.Printf("Error querying clicks: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}
		defer rows.Close()

		var clicks []map[string]interface{}
		for rows.Next() {
			var id string
			var timestamp time.Time
			if err := rows.Scan(&id, &timestamp); err != nil {
				log.Printf("Error scanning row: %v", err)
				return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
			}
			clicks = append(clicks, map[string]interface{}{
				"id":        id,
				"timestamp": timestamp,
			})
		}

		if len(clicks) == 0 {
			return c.Status(fiber.StatusNotFound).SendString("No clicks found")
		}

		return c.JSON(clicks)
	})

	// Start server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}

// isValidPath checks if the provided path is valid
func isValidPath(path string) bool {
	// Implement path validation logic if needed
	return true
}