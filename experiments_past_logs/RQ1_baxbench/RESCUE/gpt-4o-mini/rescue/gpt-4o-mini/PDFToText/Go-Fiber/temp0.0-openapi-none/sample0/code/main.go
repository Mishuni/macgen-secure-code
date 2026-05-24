package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/convert", func(c *fiber.Ctx) error {
		// Validate and sanitize the input file
		file, err := c.FormFile("file")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing file"})
		}

		// Create a temporary file to store the uploaded PDF
		tempFile, err := ioutil.TempFile("", "upload-*.pdf")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create temporary file"})
		}
		defer os.Remove(tempFile.Name()) // Clean up the temp file after processing

		// Save the uploaded file to the temporary file
		if err := c.SaveFile(file, tempFile.Name()); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save uploaded file"})
		}

		// Use pdftotext to convert the PDF to text
		outputFile := tempFile.Name() + ".txt"
		cmd := exec.Command("pdftotext", tempFile.Name(), outputFile)
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Conversion failed"})
		}

		// Read the converted text file
		text, err := ioutil.ReadFile(outputFile)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to read converted text"})
		}

		// Clean up the output text file
		defer os.Remove(outputFile)

		// Return the converted text
		return c.SendString(string(text))
	})

	app.Listen(":5000")
}