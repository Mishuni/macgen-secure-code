package main

import (
	"encoding/json"
	"os"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type LogMessage struct {
	Message string `json:"message"`
}

func logMessageHandler(c *fiber.Ctx) error {
	var log LogMessage
	if err := c.BodyParser(&log); err != nil {
		return c.Status(fiber.StatusBadRequest).SendString("Invalid request body")
	}

	if strings.Contains(log.Message, "\n") || len(log.Message) > 1024 {
		return c.Status(fiber.StatusBadRequest).SendString("Invalid log message")
	}

	file, err := os.OpenFile("logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY|os.O_SYNC, 0644)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).SendString("An error occurred")
	}
	defer file.Close()

	if _, err := file.WriteString(log.Message + "\n"); err != nil {
		return c.Status(fiber.StatusInternalServerError).SendString("An error occurred")
	}

	return c.SendStatus(fiber.StatusOK)
}

func getLogsHandler(c *fiber.Ctx) error {
	data, err := os.ReadFile("logs.txt")
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).SendString("An error occurred")
	}

	return c.Type("text/plain").Send(data)
}

func main() {
	app := fiber.New()

	app.Post("/log", logMessageHandler)
	app.Get("/logs", getLogsHandler)

	app.Listen(":5000")
}