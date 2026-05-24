package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"

	"github.com/gofiber/fiber/v2"
)

const songsDir = "/var/songs/"

type RequestBody struct {
	Filename string `json:"filename"`
}

func main() {
	app := fiber.New()

	app.Post("/download", func(c *fiber.Ctx) error {
		var reqBody RequestBody

		// Validate content type
		if c.Get("Content-Type") != "application/json" {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid content-type"})
		}

		// Parse the JSON request body
		if err := c.BodyParser(&reqBody); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		// Validate filename to prevent directory traversal
		if filepath.Base(reqBody.Filename) != reqBody.Filename {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid filename"})
		}

		// Construct the full file path
		fullPath := filepath.Join(songsDir, reqBody.Filename)

		// Check if the file exists
		if _, err := os.Stat(fullPath); os.IsNotExist(err) {
			return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "File does not exist"})
		}

		// Stream the file content
		c.Set("Content-Type", "audio/mpeg")
		return c.SendFile(fullPath, false)
	})

	app.Listen(":5000")
}