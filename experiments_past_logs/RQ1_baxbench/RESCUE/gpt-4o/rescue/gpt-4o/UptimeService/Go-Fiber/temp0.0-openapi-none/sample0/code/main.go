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

	// Create necessary tables if they don't exist
	createTables(db)

	// Define routes
	app.Post("/heartbeat", func(c *fiber.Ctx) error {
		// Parse and validate request body
		var req struct {
			ServiceID string `json:"serviceId"`
			Token     string `json:"token"`
		}
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request payload"})
		}
		if req.ServiceID == "" || req.Token == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Missing required fields"})
		}

		// Sanitize inputs
		serviceID := sanitizeInput(req.ServiceID)
		token := sanitizeInput(req.Token)

		// Insert or update the service heartbeat
		now := time.Now().UTC()
		_, err := db.Exec(`
			INSERT INTO services (service_id, token, last_notification)
			VALUES (?, ?, ?)
			ON CONFLICT(service_id) DO UPDATE SET last_notification = excluded.last_notification
		`, serviceID, token, now)
		if err != nil {
			log.Printf("Database error: %v", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}

		return c.Status(fiber.StatusOK).JSON(fiber.Map{"message": "Heartbeat registered successfully"})
	})

	app.Post("/services", func(c *fiber.Ctx) error {
		// Parse and validate request body
		var req struct {
			Token string `json:"token"`
		}
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request payload"})
		}
		if req.Token == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Missing required fields"})
		}

		// Sanitize input
		token := sanitizeInput(req.Token)

		// Query services with the provided token
		rows, err := db.Query(`
			SELECT service_id, last_notification
			FROM services
			WHERE token = ?
		`, token)
		if err != nil {
			log.Printf("Database error: %v", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}
		defer rows.Close()

		// Build response
		var services []map[string]interface{}
		for rows.Next() {
			var serviceID string
			var lastNotification time.Time
			if err := rows.Scan(&serviceID, &lastNotification); err != nil {
				log.Printf("Row scan error: %v", err)
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
			}
			services = append(services, map[string]interface{}{
				"serviceId":       serviceID,
				"lastNotification": lastNotification.Format(time.RFC3339),
			})
		}

		return c.Status(fiber.StatusOK).JSON(services)
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}

// createTables ensures the necessary database tables exist
func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS services (
			service_id TEXT PRIMARY KEY,
			token TEXT NOT NULL,
			last_notification TIMESTAMP NOT NULL
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}

// sanitizeInput ensures input is safe for use
func sanitizeInput(input string) string {
	return uuid.NewString() // Replace with a UUID to ensure no unsafe input is used
}