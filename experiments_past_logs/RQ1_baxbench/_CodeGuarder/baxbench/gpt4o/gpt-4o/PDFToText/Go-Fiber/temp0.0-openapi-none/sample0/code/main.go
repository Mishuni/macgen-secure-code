package main

import (
	"bytes"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"

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

		// Retrieve the file from the form:
		files := form.File["file"]
		if len(files) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "No file uploaded",
			})
		}

		// Process the first file:
		file := files[0]
		filePath := filepath.Join(os.TempDir(), file.Filename)

		// Save the file to a temporary location:
		if err := c.SaveFile(file, filePath); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to save file",
			})
		}
		defer os.Remove(filePath) // Clean up the file after processing

		// Convert PDF to text using pdftotext:
		text, err := convertPDFToText(filePath)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Conversion failed",
			})
		}

		// Return the converted text:
		return c.SendString(text)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

// convertPDFToText uses the pdftotext utility to convert a PDF file to plain text.
func convertPDFToText(filePath string) (string, error) {
	cmd := exec.Command("pdftotext", filePath, "-")
	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &out

	if err := cmd.Run(); err != nil {
		return "", fmt.Errorf("pdftotext error: %v", err)
	}

	return out.String(), nil
}