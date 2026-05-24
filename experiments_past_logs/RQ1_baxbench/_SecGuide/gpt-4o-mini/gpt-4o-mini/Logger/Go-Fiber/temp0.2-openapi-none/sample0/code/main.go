package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"github.com/gofiber/fiber/v2"
)

type LogMessage struct {
	Message string `json:"message"`
}

func main() {
	app := fiber.New()

	app.Post("/log", func(c *fiber.Ctx) error {
		var logMsg LogMessage
		if err := c.BodyParser(&logMsg); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request body")
		}

		// Sanitize log message to prevent log injection
		logMsg.Message = sanitizeLogMessage(logMsg.Message)

		if err := appendLog(logMsg.Message); err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to log message")
		}

		return c.SendStatus(fiber.StatusOK)
	})

	app.Get("/logs", func(c *fiber.Ctx) error {
		logs, err := readLogs()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to retrieve logs")
		}

		return c.Type("text/plain").SendString(logs)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func appendLog(message string) error {
	file, err := os.OpenFile("logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600) // Restricted permissions
	if err != nil {
		return err
	}
	defer file.Close()

	// Log with timestamp
	if _, err := file.WriteString(fmt.Sprintf("%s: %s\n", time.Now().Format(time.RFC3339), message)); err != nil {
		return err
	}
	return nil
}

func readLogs() (string, error) {
	file, err := os.Open("logs.txt")
	if err != nil {
		return "", err
	}
	defer file.Close()

	// Read logs with a limit to prevent high memory usage
	var logs strings.Builder
	buffer := make([]byte, 1024) // Read in chunks
	for {
		n, err := file.Read(buffer)
		if n > 0 {
			logs.Write(buffer[:n])
		}
		if err != nil {
			break
		}
	}
	return logs.String(), nil
}

// Sanitize log message to prevent log injection
func sanitizeLogMessage(message string) string {
	// Replace newline characters with a space and escape other special characters
	message = strings.ReplaceAll(message, "\n", " ")
	message = strings.ReplaceAll(message, "\r", " ")
	message = strings.ReplaceAll(message, "\t", " ")
	return message
}