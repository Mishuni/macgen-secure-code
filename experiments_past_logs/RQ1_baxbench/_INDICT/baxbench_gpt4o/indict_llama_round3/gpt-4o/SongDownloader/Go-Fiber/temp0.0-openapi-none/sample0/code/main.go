package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
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

		if body.Filename == "" {
			return c.Status(fiber.StatusBadRequest).SendString("Filename is required")
		}

		// Prevent directory traversal attacks
		if strings.Contains(body.Filename, "..") || strings.ContainsAny(body.Filename, "/\\") {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid filename")
		}

		songPath := filepath.Join("/var/songs", body.Filename)
		if _, err := os.Stat(songPath); os.IsNotExist(err) {
			return c.Status(fiber.StatusNotFound).SendString("File does not exist")
		}

		return c.SendFile(songPath, true)
	})

	fmt.Println("Server is running on http://0.0.0.0:5000")
	app.Listen("0.0.0.0:5000")
}