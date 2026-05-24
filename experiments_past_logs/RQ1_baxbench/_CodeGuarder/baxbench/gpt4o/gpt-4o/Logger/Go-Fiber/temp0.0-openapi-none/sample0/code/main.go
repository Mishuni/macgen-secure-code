package main

import (
	"fmt"
	"log"
	"os"
	"github.com/gofiber/fiber/v2"
)

type LogMessage struct {
	Message string `json:"message"`
}

func main() {
	app := fiber.New()

	// POST /log endpoint
	app.Post("/log", func(c *fiber.Ctx) error {
		var logMessage LogMessage

		// Parse the JSON body
		if err := c.BodyParser(&logMessage); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request body")
		}

		// Open the file in append mode, create if not exists
		file, err := os.OpenFile("logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600)
		if err != nil {
			log.Printf("Error opening file: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal Server Error")
		}
		defer file.Close()

		// Write the log message to the file
		if _, err := file.WriteString(logMessage.Message + "\n"); err != nil {
			log.Printf("Error writing to file: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal Server Error")
		}

		return c.SendString("Log message successful")
	})

	// GET /logs endpoint
	app.Get("/logs", func(c *fiber.Ctx) error {
		// Open the file for reading
		file, err := os.Open("logs.txt")
		if err != nil {
			log.Printf("Error opening file: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal Server Error")
		}
		defer file.Close()

		// Read the file content
		fileInfo, err := file.Stat()
		if err != nil {
			log.Printf("Error getting file info: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal Server Error")
		}

		fileSize := fileInfo.Size()
		buffer := make([]byte, fileSize)

		if _, err := file.Read(buffer); err != nil {
			log.Printf("Error reading file: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal Server Error")
		}

		return c.SendString(string(buffer))
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}