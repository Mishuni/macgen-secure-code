package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type RequestBody struct {
	Filename string `json:"filename"`
}

func isValidFileType(filename string) bool {
	allowedExtensions := []string{".mp3", ".wav", ".ogg"}
	for _, ext := range allowedExtensions {
		if strings.HasSuffix(filename, ext) {
			return true
		}
	}
	return false
}

func sanitizeFilename(filename string) string {
	// Remove any control characters and ensure the filename is safe
	return filepath.Base(filename)
}

func main() {
	app := fiber.New()

	app.Post("/download", func(c *fiber.Ctx) error {
		var requestBody RequestBody
		if err := c.BodyParser(&requestBody); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Validate filename to prevent directory traversal attacks
		if strings.Contains(requestBody.Filename, "..") || strings.ContainsAny(requestBody.Filename, "\x00") {
			return c.Status(http.StatusBadRequest).SendString("Invalid filename")
		}

		// Validate file type
		if !isValidFileType(requestBody.Filename) {
			return c.Status(http.StatusBadRequest).SendString("Invalid file type")
		}

		filePath := filepath.Join("/var/songs", requestBody.Filename)
		file, err := os.Open(filePath)
		if err != nil {
			if os.IsNotExist(err) {
				return c.Status(http.StatusNotFound).SendString("File does not exist")
			}
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}
		defer file.Close()

		// Sanitize filename for Content-Disposition header
		sanitizedFilename := sanitizeFilename(requestBody.Filename)
		c.Set("Content-Type", "application/octet-stream")
		c.Set("Content-Disposition", "attachment; filename=\""+sanitizedFilename+"\"")
		return c.SendStream(file)
	})

	app.Listen(":5000")
}