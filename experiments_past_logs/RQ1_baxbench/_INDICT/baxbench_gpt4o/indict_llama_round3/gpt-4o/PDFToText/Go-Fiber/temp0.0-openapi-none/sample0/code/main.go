package main

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/convert", func(c *fiber.Ctx) error {
		// Parse the multipart form:
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid input or missing file",
			})
		}

		// Get the file from the form:
		files := form.File["file"]
		if len(files) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "No file uploaded",
			})
		}

		// Open the uploaded file:
		file, err := files[0].Open()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to open uploaded file",
			})
		}
		defer file.Close()

		// Create a temporary file to save the uploaded PDF:
		tempFile, err := os.CreateTemp("", "uploaded-*.pdf")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to create temporary file",
			})
		}
		defer os.Remove(tempFile.Name())
		defer tempFile.Close()

		// Write the uploaded file to the temporary file:
		if _, err := file.Seek(0, 0); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to read uploaded file",
			})
		}
		if _, err := tempFile.ReadFrom(file); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to save uploaded file",
			})
		}

		// Use pdftotext to convert the PDF to text:
		cmd := exec.Command("pdftotext", tempFile.Name(), "-")
		var out bytes.Buffer
		cmd.Stdout = &out
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Conversion failed",
			})
		}

		// Return the converted text:
		return c.SendString(out.String())
	})

	// Start the server on port 5000:
	if err := app.Listen("0.0.0.0:5000"); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}