package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Click struct {
	ID        string    `json:"id"`
	Timestamp time.Time `json:"timestamp"`
}

func main() {
	app := fiber.New()

	// Retrieve the application secret from the environment variable
	appSecret := os.Getenv("APP_SECRET")
	if appSecret == "" {
		log.Fatal("APP_SECRET environment variable is required")
	}

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create the clicks table if it doesn't exist
	createTableSQL := `CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME
	);`
	if _, err := db.Exec(createTableSQL); err != nil {
		log.Fatal(err)
	}

	// Endpoint to register a click
	app.Post("/click", func(c *fiber.Ctx) error {
		click := Click{
			ID:        uuid.NewString(),
			Timestamp: time.Now(),
		}

		// Insert the click into the database
		insertSQL := `INSERT INTO clicks (id, timestamp) VALUES (?, ?)`
		if _, err := db.Exec(insertSQL, click.ID, click.Timestamp); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
		}

		return c.Status(http.StatusCreated).JSON(click)
	})

	// Endpoint to retrieve clicks
	app.Get("/clicks", func(c *fiber.Ctx) error {
		date := c.Query("date")
		direction := c.Query("direction")

		if date == "" || (direction != "<" && direction != ">" && direction != "<=" && direction != ">=") {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
		}

		var query string
		switch direction {
		case "<":
			query = "SELECT id, timestamp FROM clicks WHERE timestamp < ?"
		case ">":
			query = "SELECT id, timestamp FROM clicks WHERE timestamp > ?"
		case "<=":
			query = "SELECT id, timestamp FROM clicks WHERE timestamp <= ?"
		case ">=":
			query = "SELECT id, timestamp FROM clicks WHERE timestamp >= ?"
		}

		rows, err := db.Query(query, date)
		if err != nil {
			return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "No clicks found"})
		}
		defer rows.Close()

		var clicks []Click
		for rows.Next() {
			var click Click
			if err := rows.Scan(&click.ID, &click.Timestamp); err != nil {
				return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
			}
			clicks = append(clicks, click)
		}

		if len(clicks) == 0 {
			return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "No clicks found"})
		}

		return c.Status(http.StatusOK).JSON(clicks)
	})

	// Start the server
	log.Fatal(app.Listen(":5000"))
}