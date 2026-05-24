package main

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/h2non/filetype"
)

func isValidPDF(file *multipart.FileHeader) bool {
	// Check the file extension
	ext := filepath.Ext(file.Filename)
	if ext != ".pdf" {
		return false
	}

	// Check the MIME type using filetype package
	return file.Header.Get("Content-Type") == "application/pdf"
}

func convertPDFToText(tempFileName string) (string, error) {
	// Create a command to execute pdftotext with a timeout
	cmd := exec.Command("pdftotext", tempFileName, "-")
	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &out

	// Set a timeout for the command execution
	if err := cmd.Start(); err != nil {
		return "", err
	}

	// Wait for the command to finish with a timeout
	done := make(chan error)
	go func() {
		done <- cmd.Wait()
	}()

	select {
	case err := <-done:
		if err != nil {
			return "", err
		}
	case <-time.After(10 * time.Second): // Timeout after 10 seconds
		cmd.Process.Kill()
		return "", fmt.Errorf("command timed out")
	}

	return out.String(), nil
}

func main() {
	app := fiber.New()

	app.Post("/convert", func(c *fiber.Ctx) error {
		// Parse the multipart form
		if err := c.BodyParser(&fiber.Map{}); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing file"})
		}

		// Save the uploaded file
		file, err := c.FormFile("file")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input or missing file"})
		}

		// Validate the uploaded file
		if !isValidPDF(file) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Uploaded file is not a valid PDF"})
		}

		// Create a temporary file to save the uploaded PDF
		tempFile, err := ioutil.TempFile(os.TempDir(), "upload-*.pdf")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Internal Server Error - Unable to create temp file"})
		}
		defer os.Remove(tempFile.Name()) // Clean up the temp file

		// Save the uploaded file to the temp file
		if err := c.SaveFile(file, tempFile.Name()); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Internal Server Error - Unable to save file"})
		}

		// Convert PDF to text
		output, err := convertPDFToText(tempFile.Name())
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Internal Server Error - Conversion failed"})
		}

		// Return the converted text
		return c.SendString(output)
	})

	// Start the server on port 5000
	app.Listen(":5000")
}