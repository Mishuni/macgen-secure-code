package main

import (
	"database/sql"
	"log"
	"net/http"
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
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create clicks table if it doesn't exist
	createTableSQL := `CREATE TABLE IF NOT EXISTS clicks (
		id TEXT PRIMARY KEY,
		timestamp DATETIME
	);`
	if _, err := db.Exec(createTableSQL); err != nil {
		log.Fatal(err)
	}

	app.Post("/click", func(c *fiber.Ctx) error {
		click := Click{
			ID:        uuid.NewString(),
			Timestamp: time.Now().UTC(),
		}

		// Insert click into database
		_, err := db.Exec("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", click.ID, click.Timestamp)
		if err != nil {
			log.Println("Error inserting click:", err)
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}

		return c.Status(http.StatusCreated).JSON(click)
	})

	app.Get("/clicks", func(c *fiber.Ctx) error {
		date := c.Query("date")
		direction := c.Query("direction")

		if date == "" || direction == "" {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
		}

		// Validate direction against allowed operators
		allowedOperators := map[string]bool{"<": true, "<=": true, ">": true, ">=": true}
		if !allowedOperators[direction] {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid direction"})
		}

		// Validate date format
		if _, err := time.Parse(time.RFC3339, date); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid date format"})
		}

		// Use parameterized query to prevent SQL injection
		query := "SELECT id, timestamp FROM clicks WHERE timestamp " + direction + " ?"
		rows, err := db.Query(query, date)
		if err != nil {
			log.Println("Error querying clicks:", err)
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}
		defer rows.Close()

		var clicks []Click
		for rows.Next() {
			var click Click
			if err := rows.Scan(&click.ID, &click.Timestamp); err != nil {
				log.Println("Error scanning click:", err)
				return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
			}
			clicks = append(clicks, click)
		}

		if len(clicks) == 0 {
			return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "No clicks found"})
		}

		return c.JSON(clicks)
	})

	log.Fatal(app.Listen(":5000"))
}