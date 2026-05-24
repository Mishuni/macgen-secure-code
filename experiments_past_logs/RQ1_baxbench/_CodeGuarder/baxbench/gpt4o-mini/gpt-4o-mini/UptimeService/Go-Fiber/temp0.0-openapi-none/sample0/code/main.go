package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type Service struct {
	ServiceID       string `json:"serviceId"`
	LastNotification string `json:"lastNotification"`
	Token           string `json:"token"`
}

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS services (
		serviceId TEXT NOT NULL PRIMARY KEY,
		lastNotification TEXT,
		token TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func registerHeartbeat(c *fiber.Ctx) error {
	var service Service
	if err := c.BodyParser(&service); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request payload."})
	}

	if service.ServiceID == "" || service.Token == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "serviceId and token are required."})
	}

	_, err := db.Exec(`INSERT OR REPLACE INTO services (serviceId, lastNotification, token) VALUES (?, datetime('now'), ?)`,
		service.ServiceID, service.Token)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error."})
	}

	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "Heartbeat registered successfully."})
}

func getServices(c *fiber.Ctx) error {
	var request struct {
		Token string `json:"token"`
	}
	if err := c.BodyParser(&request); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request payload."})
	}

	if request.Token == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "token is required."})
	}

	rows, err := db.Query(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, request.Token)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error."})
	}
	defer rows.Close()

	var services []Service
	for rows.Next() {
		var service Service
		if err := rows.Scan(&service.ServiceID, &service.LastNotification); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error."})
		}
		services = append(services, service)
	}

	return c.Status(http.StatusOK).JSON(services)
}

func main() {
	app := fiber.New()

	initDB()
	defer db.Close()

	app.Post("/heartbeat", registerHeartbeat)
	app.Post("/services", getServices)

	log.Fatal(app.Listen(":5000"))
}