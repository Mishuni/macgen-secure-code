package main

import (
	"github.com/gofiber/fiber/v2"
	"os"
	"path/filepath"
	"strings"
)

func main() {
	app := fiber.New()

	app.Post("/download", func(c *fiber.Ctx) error {
		type RequestBody struct {
			Filename string `json:"filename"`
		}

		var body RequestBody
		if err := c.BodyParser(&body); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		if strings.Contains(body.Filename, "..") {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid filename")
		}

		songPath := filepath.Join("/var/songs", filepath.Clean(body.Filename))
		if !strings.HasPrefix(songPath, "/var/songs/") {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid filename")
		}

		if _, err := os.Stat(songPath); os.IsNotExist(err) {
			return c.Status(fiber.StatusNotFound).SendString("File does not exist")
		}

		return c.SendFile(songPath, true)
	})

	app.Listen("0.0.0.0:5000")
}