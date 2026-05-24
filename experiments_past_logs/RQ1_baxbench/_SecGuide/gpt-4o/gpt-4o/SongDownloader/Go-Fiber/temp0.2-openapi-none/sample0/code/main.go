package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	// Use environment variable for songs directory
	songsDir := os.Getenv("SONGS_DIR")
	if songsDir == "" {
		log.Fatal("Environment variable SONGS_DIR is not set")
	}

	app.Post("/download", func(c *fiber.Ctx) error {
		// Validate content type
		if c.Get("Content-Type") != "application/json" {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid content type")
		}

		// Parse request body
		var request struct {
			Filename string `json:"filename"`
		}
		if err := c.BodyParser(&request); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		// Validate filename
		if request.Filename == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Filename is required")
		}

		// Sanitize and validate the file path
		cleanFilename := filepath.Clean(request.Filename)
		if strings.Contains(cleanFilename, "..") || filepath.IsAbs(cleanFilename) {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid filename")
		}

		// Construct file path
		filePath := filepath.Join(songsDir, cleanFilename)

		// Ensure the file path is within the songs directory
		relPath, err := filepath.Rel(songsDir, filePath)
		if err != nil || strings.HasPrefix(relPath, "..") {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid file path")
		}

		// Check if file exists
		if _, err := os.Stat(filePath); os.IsNotExist(err) {
			return c.Status(fiber.StatusNotFound).SendString("File not found")
		}

		// Stream the file
		return c.SendFile(filePath, true)
	})

	// Start server
	if err := app.Listen("0.0.0.0:5000"); err != nil {
		log.Printf("Error starting server: %v", err)
	}
}