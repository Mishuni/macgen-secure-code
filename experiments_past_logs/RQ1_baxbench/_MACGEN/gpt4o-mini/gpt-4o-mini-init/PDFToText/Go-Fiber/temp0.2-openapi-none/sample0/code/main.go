package main

import (
	"bytes"
	"context"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"time"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/convert", func(c *fiber.Ctx) error {
		// Parse the multipart form
		if err := c.BodyParser(&fiber.Map{}); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		// Get the file from the form
		file, err := c.FormFile("file")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Missing file"})
		}

		// Save the file temporarily
		tempFile, err := ioutil.TempFile("", "upload-*.pdf")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create temporary file"})
		}
		defer os.Remove(tempFile.Name()) // Clean up the temporary file

		if err := c.SaveFile(file, tempFile.Name()); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save file"})
		}

		// Validate the file type
		buff := make([]byte, 512)
		tempFile.Seek(0, 0) // Reset file pointer to the beginning
		if _, err := tempFile.Read(buff); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to read file"})
		}
		if http.DetectContentType(buff) != "application/pdf" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid file type"})
		}

		// Use pdftotext to convert PDF to text
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		cmd := exec.CommandContext(ctx, "pdftotext", tempFile.Name(), "-")
		var out bytes.Buffer
		cmd.Stdout = &out
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Conversion failed"})
		}

		// Return the converted text
		return c.SendString(out.String())
	})

	app.Listen(":5000")
}