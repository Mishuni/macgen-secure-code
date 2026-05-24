package main

import (
	"github.com/gofiber/fiber/v2"
	"log"
	"os"
	"sync"
)

var mu sync.Mutex

func main() {
	app := fiber.New()

	// Route to log a message
	app.Post("/log", func(c *fiber.Ctx) error {
		type Request struct {
			Message string `json:"message"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request body")
		}

		// Basic input validation
		if req.Message == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Message cannot be empty")
		}

		mu.Lock()
		defer mu.Unlock()

		file, err := os.OpenFile("logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to open log file")
		}
		defer file.Close()

		if _, err := file.WriteString(req.Message + "\n"); err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to write log")
		}

		return c.SendString("Log message successful")
	})

	// Route to retrieve logs
	app.Get("/logs", func(c *fiber.Ctx) error {
		mu.Lock()
		defer mu.Unlock()

		data, err := os.ReadFile("logs.txt")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to read logs")
		}

		return c.Type("text/plain").Send(data)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}