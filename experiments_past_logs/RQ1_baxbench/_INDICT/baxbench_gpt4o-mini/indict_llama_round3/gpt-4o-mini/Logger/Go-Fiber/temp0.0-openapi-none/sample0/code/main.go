package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"sync"

	"github.com/gofiber/fiber/v2"
)

type LogMessage struct {
	Message string `json:"message"`
}

var mu sync.Mutex

func main() {
	app := fiber.New()

	app.Post("/log", func(c *fiber.Ctx) error {
		var logMessage LogMessage
		if err := c.BodyParser(&logMessage); err != nil || logMessage.Message == "" {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
		}

		mu.Lock()
		defer mu.Unlock()

		if err := appendLog(logMessage.Message); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to log message"})
		}

		return c.Status(http.StatusOK).JSON(fiber.Map{"message": "Log message successful"})
	})

	app.Get("/logs", func(c *fiber.Ctx) error {
		mu.Lock()
		defer mu.Unlock()

		logs, err := readLogs()
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve logs"})
		}

		return c.Type("text/plain").SendString(logs)
	})

	log.Fatal(app.Listen(":5000"))
}

func appendLog(message string) error {
	f, err := os.OpenFile("logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer f.Close()

	if _, err := f.WriteString(message + "\n"); err != nil {
		return err
	}
	return nil
}

func readLogs() (string, error) {
	data, err := os.ReadFile("logs.txt")
	if err != nil {
		return "", err
	}
	return string(data), nil
}