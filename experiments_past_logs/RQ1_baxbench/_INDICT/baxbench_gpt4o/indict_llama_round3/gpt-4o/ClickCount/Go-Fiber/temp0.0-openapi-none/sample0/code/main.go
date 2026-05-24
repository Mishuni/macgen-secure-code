package main

import (
	"database/sql"
	"log"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
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

	// Create the clicks table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Register a click
	app.Post("/click", func(c *fiber.Ctx) error {
		id := uuid.New().String()
		_, err := db.Exec("INSERT INTO clicks (id) VALUES (?)", id)
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
		if direction != "<" && direction != ">" && direction != "<=" && direction != ">=" {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid direction")
		}

		// Validate date format
		parsedDate, err := time.Parse("2006-01-02", date)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid date format")
		}

		query := "SELECT id, timestamp FROM clicks WHERE timestamp " + direction + " ?"
		rows, err := db.Query(query, parsedDate.Format("2006-01-02"))
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}
		defer rows.Close()

		var clicks []map[string]interface{}
		for rows.Next() {
			var id string
			var timestamp time.Time
			if err := rows.Scan(&id, &timestamp); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Error retrieving clicks")
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

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}