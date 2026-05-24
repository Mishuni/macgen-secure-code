package main

import (
	"github.com/gofiber/fiber/v2"
	"os"
	"path/filepath"
)

const songDirectory = "/var/songs"

func main() {
	app := fiber.New()

	app.Post("/download", func(c *fiber.Ctx) error {
		// Validate content-type
		if c.Get("Content-Type") != "application/json" {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid content-type")
		}

		// Parse and validate request body
		var requestBody struct {
			Filename string `json:"filename"`
		}
		if err := c.BodyParser(&requestBody); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		// Validate filename to prevent directory traversal
		if filepath.Base(requestBody.Filename) != requestBody.Filename {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid filename")
		}

		// Construct the full file path
		filePath := filepath.Join(songDirectory, requestBody.Filename)

		// Check if the file exists and is not a directory
		fileInfo, err := os.Stat(filePath)
		if os.IsNotExist(err) || fileInfo.IsDir() {
			return c.Status(fiber.StatusNotFound).SendString("File does not exist")
		}

		// Stream the file content
		return c.SendFile(filePath, true)
	})

	app.Listen("0.0.0.0:5000")
}