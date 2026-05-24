package main

import (
	"github.com/gofiber/fiber/v2"
	"log"
	"os"
	"strings"
)

func main() {
	app := fiber.New()

	app.Post("/log", func(c *fiber.Ctx) error {
		type Request struct {
			Message string `json:"message"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		// Sanitize and validate the input to prevent log injection
		sanitizedMessage := sanitizeAndValidateInput(req.Message)
		if sanitizedMessage == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid message content")
		}

		if err := logMessage(sanitizedMessage); err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to log message")
		}

		return c.SendString("Log message successful")
	})

	// Remove the /logs endpoint to prevent log file exposure

	log.Fatal(app.Listen("127.0.0.1:5000")) // Bind to localhost for security
}

func logMessage(message string) error {
	// Use environment variable for log file path
	logFileName := os.Getenv("LOG_FILE_PATH")
	if logFileName == "" {
		logFileName = "logs.txt" // Default to logs.txt if not set
	}

	// Use more restrictive file permissions
	file, err := os.OpenFile(logFileName, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600)
	if err != nil {
		return err
	}
	defer file.Close()

	logger := log.New(file, "", log.LstdFlags)
	logger.Println(message)
	return nil
}

func sanitizeAndValidateInput(input string) string {
	// Comprehensive sanitization and validation
	sanitized := strings.TrimSpace(input)
	if strings.ContainsAny(sanitized, "\n\r\t") {
		return ""
	}
	return sanitized
}