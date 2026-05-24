package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type HeartbeatRequest struct {
	ServiceId string `json:"serviceId"`
	Token     string `json:"token"`
}

type ServicesRequest struct {
	Token string `json:"token"`
}

type ServiceStatus struct {
	ServiceId        string `json:"serviceId"`
	LastNotification string `json:"lastNotification"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS services (
		id TEXT PRIMARY KEY,
		token TEXT,
		last_notification DATETIME
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func registerHeartbeat(c *fiber.Ctx) error {
	var req HeartbeatRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request payload."})
	}

	_, err := db.Exec("INSERT OR REPLACE INTO services (id, token, last_notification) VALUES (?, ?, datetime('now'))", req.ServiceId, req.Token)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error."})
	}

	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "Heartbeat registered successfully."})
}

func getServices(c *fiber.Ctx) error {
	var req ServicesRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request payload."})
	}

	rows, err := db.Query("SELECT id, last_notification FROM services WHERE token = ?", req.Token)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error."})
	}
	defer rows.Close()

	var services []ServiceStatus
	for rows.Next() {
		var service ServiceStatus
		if err := rows.Scan(&service.ServiceId, &service.LastNotification); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error."})
		}
		services = append(services, service)
	}

	return c.Status(http.StatusOK).JSON(services)
}

func main() {
	app := fiber.New()

	app.Post("/heartbeat", registerHeartbeat)
	app.Post("/services", getServices)

	log.Fatal(app.Listen(":5000"))
}