package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

const dbName = "db.sqlite3"

func main() {
	app := fiber.New()

	// Initialize the database
	db, err := sql.Open("sqlite3", dbName)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create the services table if it doesn't exist
	createTableQuery := `
	CREATE TABLE IF NOT EXISTS services (
		serviceId TEXT PRIMARY KEY,
		token TEXT NOT NULL,
		lastNotification DATETIME
	);`
	if _, err := db.Exec(createTableQuery); err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Register the /heartbeat endpoint
	app.Post("/heartbeat", func(c *fiber.Ctx) error {
		var payload struct {
			ServiceId string `json:"serviceId"`
			Token     string `json:"token"`
		}

		if err := c.BodyParser(&payload); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request payload")
		}

		if payload.ServiceId == "" || payload.Token == "" {
			return c.Status(fiber.StatusBadRequest).SendString("ServiceId and Token are required")
		}

		// Update or insert the service's last notification date
		now := time.Now().UTC()
		_, err := db.Exec(`
			INSERT INTO services (serviceId, token, lastNotification) 
			VALUES (?, ?, ?)
			ON CONFLICT(serviceId) DO UPDATE SET 
			lastNotification=excluded.lastNotification, token=excluded.token;`,
			payload.ServiceId, payload.Token, now)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}

		return c.SendString("Heartbeat registered successfully")
	})

	// Register the /services endpoint
	app.Post("/services", func(c *fiber.Ctx) error {
		var payload struct {
			Token string `json:"token"`
		}

		if err := c.BodyParser(&payload); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request payload")
		}

		if payload.Token == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Token is required")
		}

		rows, err := db.Query("SELECT serviceId, lastNotification FROM services WHERE token = ?", payload.Token)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}
		defer rows.Close()

		var services []map[string]interface{}
		for rows.Next() {
			var serviceId string
			var lastNotification time.Time
			if err := rows.Scan(&serviceId, &lastNotification); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
			}
			services = append(services, map[string]interface{}{
				"serviceId":       serviceId,
				"lastNotification": lastNotification,
			})
		}

		return c.JSON(services)
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}