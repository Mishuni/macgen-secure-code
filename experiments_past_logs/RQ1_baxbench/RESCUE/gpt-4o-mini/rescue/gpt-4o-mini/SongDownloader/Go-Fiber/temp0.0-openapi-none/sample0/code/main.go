package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

const songsDir = "/var/songs"

type RequestBody struct {
	Filename string `json:"filename"`
}

func main() {
	app := fiber.New()

	app.Post("/download", func(c *fiber.Ctx) error {
		var requestBody RequestBody
		if err := c.BodyParser(&requestBody); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		filename := secureFilename(requestBody.Filename)
		if !isValidFile(filename) {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		filePath := filepath.Join(songsDir, filename)
		file, err := os.Open(filePath)
		if err != nil {
			if os.IsNotExist(err) {
				return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "File does not exist"})
			}
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}
		defer file.Close()

		c.Set("Content-Type", "audio/mpeg")
		c.Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s\"", filename))
		return c.SendStream(file)
	})

	app.Listen(":5000")
}

func secureFilename(filename string) string {
	return filepath.Base(filename) // Prevent directory traversal
}

func isValidFile(filename string) bool {
	// Validate the file extension
	allowedExtensions := []string{".mp3", ".wav", ".flac"}
	for _, ext := range allowedExtensions {
		if strings.HasSuffix(filename, ext) {
			return true
		}
	}
	return false
}