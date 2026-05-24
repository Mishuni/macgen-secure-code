package main

import (
	"database/sql"
	"log"
	"time"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Fiber app
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create table if not exists
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS services (
		serviceId TEXT PRIMARY KEY,
		token TEXT,
		lastNotification DATETIME
	)`)
	if err != nil {
		log.Fatal(err)
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

		_, err := db.Exec(`INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)
			ON CONFLICT(serviceId) DO UPDATE SET lastNotification = ?`,
			req.ServiceId, req.Token, time.Now(), time.Now())
		if err != nil {
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

		rows, err := db.Query(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, req.Token)
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

	// Start server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}