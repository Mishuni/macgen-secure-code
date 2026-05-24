package main

import (
	"github.com/gofiber/fiber/v2"
	"os"
	"path/filepath"
)

const storageDir = "/var/songs"

func main() {
	app := fiber.New()

	app.Post("/download", func(c *fiber.Ctx) error {
		// Parse the JSON body
		var requestBody struct {
			Filename string `json:"filename"`
		}
		if err := c.BodyParser(&requestBody); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		// Validate the filename
		if requestBody.Filename == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Filename is required")
		}

		// Sanitize and construct the absolute path
		absPath := filepath.Join(storageDir, filepath.Clean(requestBody.Filename))
		if !filepath.HasPrefix(absPath, storageDir) {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid filename")
		}

		// Check if the file exists
		if _, err := os.Stat(absPath); os.IsNotExist(err) {
			return c.Status(fiber.StatusNotFound).SendString("File does not exist")
		}

		// Stream the file content
		return c.SendFile(absPath, true)
	})

	// Start the server
	app.Listen("0.0.0.0:5000")
}