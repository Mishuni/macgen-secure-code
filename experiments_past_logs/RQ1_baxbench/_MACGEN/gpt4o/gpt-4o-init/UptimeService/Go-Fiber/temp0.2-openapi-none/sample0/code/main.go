package main

import (
	"database/sql"
	"log"
	"time"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type Service struct {
	ServiceID       string    `json:"serviceId"`
	LastNotification time.Time `json:"lastNotification"`
}

func main() {
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create services table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS services (
		serviceId TEXT PRIMARY KEY,
		token TEXT,
		lastNotification DATETIME
	)`)
	if err != nil {
		log.Fatal(err)
	}

	app.Post("/heartbeat", func(c *fiber.Ctx) error {
		var payload struct {
			ServiceID string `json:"serviceId"`
			Token     string `json:"token"`
		}

		if err := c.BodyParser(&payload); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request payload")
		}

		_, err := db.Exec(`INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?) 
			ON CONFLICT(serviceId) DO UPDATE SET lastNotification = ?`,
			payload.ServiceID, payload.Token, time.Now(), time.Now())
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}

		return c.SendString("Heartbeat registered successfully")
	})

	app.Post("/services", func(c *fiber.Ctx) error {
		var payload struct {
			Token string `json:"token"`
		}

		if err := c.BodyParser(&payload); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request payload")
		}

		rows, err := db.Query(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, payload.Token)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}
		defer rows.Close()

		var services []Service
		for rows.Next() {
			var service Service
			if err := rows.Scan(&service.ServiceID, &service.LastNotification); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
			}
			services = append(services, service)
		}

		return c.JSON(services)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}