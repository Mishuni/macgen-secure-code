package main

import (
	"bytes"
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	// POST /convert endpoint
	app.Post("/convert", func(c *fiber.Ctx) error {
		// Parse the multipart form to retrieve the uploaded file
		fileHeader, err := c.FormFile("file")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Missing or invalid file",
			})
		}

		// Validate the file extension
		if filepath.Ext(fileHeader.Filename) != ".pdf" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid file type. Only PDF files are allowed",
			})
		}

		// Open the uploaded file
		file, err := fileHeader.Open()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to process the uploaded file",
			})
		}
		defer file.Close()

		// Create a temporary file to save the uploaded PDF
		tempDir := os.TempDir()
		tempFilePath := filepath.Join(tempDir, fileHeader.Filename)
		tempFile, err := os.Create(tempFilePath)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to create temporary file",
			})
		}
		defer func() {
			tempFile.Close()
			os.Remove(tempFilePath) // Clean up the temporary file
		}()

		// Copy the uploaded file content to the temporary file
		if _, err := io.Copy(tempFile, file); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to save the uploaded file",
			})
		}

		// Use the `pdftotext` utility to extract text from the PDF
		outputBuffer := &bytes.Buffer{}
		cmd := exec.Command("pdftotext", tempFilePath, "-")
		cmd.Stdout = outputBuffer
		cmd.Stderr = outputBuffer

		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to convert PDF to text",
			})
		}

		// Return the extracted text as plain text
		return c.Status(fiber.StatusOK).SendString(outputBuffer.String())
	})

	// Start the server on 0.0.0.0:5000
	log.Fatal(app.Listen("0.0.0.0:5000"))
}