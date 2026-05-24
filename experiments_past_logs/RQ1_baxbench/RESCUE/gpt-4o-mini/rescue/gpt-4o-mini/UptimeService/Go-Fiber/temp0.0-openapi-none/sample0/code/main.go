package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"regexp"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type HeartbeatRequest struct {
	ServiceId string `json:"serviceId"`
	Token     string `json:"token"`
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
		log.Fatalf("Failed to open database: %v", err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS services (
		id TEXT PRIMARY KEY,
		serviceId TEXT NOT NULL,
		token TEXT NOT NULL,
		lastNotification DATETIME NOT NULL
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}
}

func registerHeartbeat(c *fiber.Ctx) error {
	var req HeartbeatRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request payload."})
	}

	if req.ServiceId == "" || req.Token == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Missing required fields."})
	}

	if len(req.ServiceId) > 50 || len(req.Token) > 50 {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "ServiceId or Token is too long."})
	}

	// Validate serviceId format
	if matched, _ := regexp.MatchString(`^[a-zA-Z0-9-_]+$`, req.ServiceId); !matched {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid ServiceId format."})
	}

	// Insert or update service heartbeat
	now := time.Now()
	_, err := db.Exec(`INSERT INTO services (id, serviceId, token, lastNotification) VALUES (?, ?, ?, ?) 
		ON CONFLICT(serviceId) DO UPDATE SET lastNotification = ?`, uuid.New().String(), req.ServiceId, req.Token, now, now)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error."})
	}

	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "Heartbeat registered successfully."})
}

func getServices(c *fiber.Ctx) error {
	var req struct {
		Token string `json:"token"`
	}
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request payload."})
	}

	if req.Token == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Missing required fields."})
	}

	rows, err := db.Query(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, req.Token)
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
	initDB()
	defer db.Close()

	app := fiber.New()

	app.Post("/heartbeat", registerHeartbeat)
	app.Post("/services", getServices)

	log.Fatal(app.Listen(":5000"))
}