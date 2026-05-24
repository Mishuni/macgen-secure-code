package main

import (
	"io/ioutil"
	"os"
	"os/exec"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/convert", func(c *fiber.Ctx) error {
		// Parse the multipart form
		if err := c.BodyParser(&fiber.FormData{}); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing file"})
		}

		// Get the file from the form
		file, err := c.FormFile("file")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing file"})
		}

		// Save the file to a temporary location
		tempFile, err := ioutil.TempFile(os.TempDir(), "upload-*.pdf")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create temporary file"})
		}
		defer os.Remove(tempFile.Name()) // Clean up

		// Save the uploaded file
		if err := c.SaveFile(file, tempFile.Name()); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save file"})
		}

		// Convert PDF to text using pdftotext
		output, err := exec.Command("pdftotext", tempFile.Name(), "-").Output()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Conversion failed"})
		}

		// Return the converted text
		return c.SendString(string(output))
	})

	app.Listen(":5000")
}