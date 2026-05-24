package main

import (
	"bufio"
	"log"
	"os"
	"sync"

	"github.com/gofiber/fiber/v2"
)

const logFileName = "logs.txt"

var mu sync.Mutex // Mutex to ensure thread-safe access to the log file

func main() {
	// Ensure the log file exists
	file, err := os.OpenFile(logFileName, os.O_CREATE|os.O_RDWR, 0644)
	if err != nil {
		log.Fatalf("Failed to create or open log file: %v", err)
	}
	file.Close()

	// Initialize Fiber app
	app := fiber.New()

	// POST /log - Log a message
	app.Post("/log", func(c *fiber.Ctx) error {
		// Parse the request body
		type LogRequest struct {
			Message string `json:"message"`
		}
		var req LogRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request body")
		}

		// Validate the message
		if req.Message == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Message cannot be empty")
		}

		// Write the log message to the file
		mu.Lock()
		defer mu.Unlock()
		file, err := os.OpenFile(logFileName, os.O_APPEND|os.O_WRONLY, 0644)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to write to log file")
		}
		defer file.Close()

		if _, err := file.WriteString(req.Message + "\n"); err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to write to log file")
		}

		return c.SendString("Log message successful")
	})

	// GET /logs - Retrieve all logged messages
	app.Get("/logs", func(c *fiber.Ctx) error {
		mu.Lock()
		defer mu.Unlock()
		file, err := os.Open(logFileName)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to read log file")
		}
		defer file.Close()

		// Read all log messages
		var logs string
		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			logs += scanner.Text() + "\n"
		}
		if err := scanner.Err(); err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to read log file")
		}

		return c.Type("text/plain").SendString(logs)
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}