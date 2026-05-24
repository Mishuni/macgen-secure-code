package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type HeartbeatRequest struct {
	ServiceId string `json:"serviceId"`
	Token     string `json:"token"`
}

type Service struct {
	ServiceId        string    `json:"serviceId"`
	LastNotification time.Time `json:"lastNotification"`
}

var db *sql.DB

func main() {
	app := fiber.New()

	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS services (
		serviceId TEXT NOT NULL,
		token TEXT NOT NULL,
		lastNotification DATETIME NOT NULL,
		PRIMARY KEY (serviceId)
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}

	app.Post("/heartbeat", registerHeartbeat)
	app.Post("/services", getServices)

	if err := app.Listen(":5000"); err != nil {
		log.Fatal(err)
	}
}

func registerHeartbeat(c *fiber.Ctx) error {
	var req HeartbeatRequest
	if err := c.BodyParser(&req); err != nil || req.ServiceId == "" || req.Token == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input."})
	}

	_, err := db.Exec("INSERT OR REPLACE INTO services (serviceId, lastNotification, token) VALUES (?, ?, ?)", req.ServiceId, time.Now(), req.Token)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error."})
	}

	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "Heartbeat registered successfully."})
}

func getServices(c *fiber.Ctx) error {
	var req struct {
		Token string `json:"token"`
	}
	if err := c.BodyParser(&req); err != nil || req.Token == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input."})
	}

	rows, err := db.Query("SELECT serviceId, lastNotification FROM services WHERE token = ?", req.Token)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error."})
	}
	defer rows.Close()

	var services []Service
	for rows.Next() {
		var service Service
		if err := rows.Scan(&service.ServiceId, &service.LastNotification); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error."})
		}
		services = append(services, service)
	}

	return c.Status(http.StatusOK).JSON(services)
}