package main

import (
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type RequestBody struct {
	Filename string `json:"filename"`
}

func isValidFilename(filename string) bool {
	// Check for path traversal by ensuring the filename does not contain any path separators
	return !strings.ContainsAny(filename, "/\\") && strings.HasSuffix(filename, ".mp3")
}

func main() {
	app := fiber.New()

	app.Post("/download", func(c *fiber.Ctx) error {
		var requestBody RequestBody
		if err := c.BodyParser(&requestBody); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		if !isValidFilename(requestBody.Filename) {
			return c.Status(http.StatusBadRequest).SendString("Invalid filename")
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

		c.Set("Content-Type", "audio/mpeg")
		c.Set("Content-Disposition", "inline; filename=\""+requestBody.Filename+"\"")
		return c.SendStream(file)
	})

	app.Listen(":5000")
}