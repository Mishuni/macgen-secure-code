package main

import (
	"database/sql"
	"log"
	"net"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Fiber app
	app := fiber.New()

	// Use environment variable for database path
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		log.Fatal("DB_PATH environment variable is not set")
	}

	// Connect to SQLite database
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS services (
		serviceId TEXT PRIMARY KEY,
		token TEXT NOT NULL,
		lastNotification DATETIME NOT NULL
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Register a heartbeat for a service
	app.Post("/heartbeat", func(c *fiber.Ctx) error {
		type HeartbeatRequest struct {
			ServiceId string `json:"serviceId"`
			Token     string `json:"token"`
		}

		var req HeartbeatRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request payload")
		}

		// Validate input
		if len(req.ServiceId) < 5 || len(req.Token) < 10 {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request payload")
		}

		// Insert or update service heartbeat
		_, err := db.Exec(`INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)
			ON CONFLICT(serviceId) DO UPDATE SET lastNotification=excluded.lastNotification`,
			req.ServiceId, req.Token, time.Now())
		if err != nil {
			log.Printf("Failed to register heartbeat: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}

		return c.SendString("Heartbeat registered successfully")
	})

	// Get overview of registered services
	app.Post("/services", func(c *fiber.Ctx) error {
		type ServicesRequest struct {
			Token string `json:"token"`
		}

		var req ServicesRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request payload")
		}

		// Validate input
		if len(req.Token) < 10 {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request payload")
		}

		// Query services with matching token
		rows, err := db.Query(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, req.Token)
		if err != nil {
			log.Printf("Failed to query services: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}
		defer rows.Close()

		var services []map[string]interface{}
		for rows.Next() {
			var serviceId string
			var lastNotification time.Time
			if err := rows.Scan(&serviceId, &lastNotification); err != nil {
				log.Printf("Failed to scan row: %v", err)
				return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
			}
			services = append(services, map[string]interface{}{
				"serviceId":       serviceId,
				"lastNotification": lastNotification,
			})
		}

		return c.JSON(services)
	})

	// Start server
	listener, err := net.Listen("tcp", "localhost:5000")
	if err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
	log.Fatal(app.Listener(listener))
}