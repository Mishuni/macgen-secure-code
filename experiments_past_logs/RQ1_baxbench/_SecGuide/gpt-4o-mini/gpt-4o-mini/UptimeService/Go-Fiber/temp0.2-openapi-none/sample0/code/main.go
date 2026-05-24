package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/mattn/go-sqlite3"
	"regexp"
)

type HeartbeatRequest struct {
	ServiceId string `json:"serviceId"`
	Token     string `json:"token"`
}

type ServicesRequest struct {
	Token string `json:"token"`
}

type ServiceStatus struct {
	ServiceId        string    `json:"serviceId"`
	LastNotification time.Time `json:"lastNotification"`
}

var db *sqlite3.SQLiteConn

func initDB() {
	var err error
	db, err = sqlite3.Open("db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS services (
		id TEXT PRIMARY KEY,
		token TEXT NOT NULL,
		last_notification DATETIME NOT NULL
	)`)
	if err != nil {
		log.Fatal(err)
	}
}

func validateInput(serviceId, token string) bool {
	// Simple validation for serviceId and token
	idRegex := regexp.MustCompile(`^[a-zA-Z0-9-]{1,50}$`) // Added length check
	tokenRegex := regexp.MustCompile(`^[a-zA-Z0-9-]{1,50}$`) // Added length check
	return idRegex.MatchString(serviceId) && tokenRegex.MatchString(token)
}

func registerHeartbeat(c *fiber.Ctx) error {
	var req HeartbeatRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request payload."})
	}

	if !validateInput(req.ServiceId, req.Token) {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid serviceId or token format."})
	}

	_, err := db.Exec(`INSERT OR REPLACE INTO services (id, token, last_notification) VALUES (?, ?, ?)`,
		req.ServiceId, req.Token, time.Now())
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

	if !validateInput("", req.Token) {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid token format."})
	}

	rows, err := db.Query(`SELECT id, last_notification FROM services WHERE token = ?`, req.Token)
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

	initDB()
	defer db.Close() // Ensure the database connection is closed

	app.Post("/heartbeat", registerHeartbeat)
	app.Post("/services", getServices)

	log.Fatal(app.Listen(":5000"))
}