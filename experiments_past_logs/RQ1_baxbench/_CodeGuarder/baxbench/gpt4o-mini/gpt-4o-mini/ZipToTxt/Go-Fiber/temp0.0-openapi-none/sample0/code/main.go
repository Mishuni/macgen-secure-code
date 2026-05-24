package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"archive/zip"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/convert", func(c *fiber.Ctx) error {
		// Handle file upload
		file, err := c.FormFile("file")
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input: file not found")
		}

		// Check if the uploaded file is a zip file
		if !strings.HasSuffix(file.Filename, ".zip") {
			return c.Status(http.StatusBadRequest).SendString("Invalid input: uploaded file is not a zip file")
		}

		// Save the uploaded zip file to a temporary location
		tempFile, err := os.CreateTemp("", "*.zip")
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to create temporary file")
		}
		defer os.Remove(tempFile.Name()) // Clean up

		if err := c.SaveFile(file, tempFile.Name()); err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to save uploaded file")
		}

		// Extract and concatenate text files
		var result strings.Builder
		if err := unzipAndConcat(tempFile.Name(), &result); err != nil {
			return c.Status(http.StatusInternalServerError).SendString(err.Error())
		}

		// Return the concatenated text
		return c.Status(http.StatusOK).SendString(result.String())
	})

	app.Listen(":5000")
}

func unzipAndConcat(zipPath string, result *strings.Builder) error {
	r, err := zip.OpenReader(zipPath)
	if err != nil {
		return fmt.Errorf("failed to open zip file: %w", err)
	}
	defer r.Close()

	for _, f := range r.File {
		// Check for Zip Slip vulnerability
		if !isValidZipEntry(f.Name) {
			return fmt.Errorf("detected Zip Slip vulnerability: %s", f.Name)
		}

		if !f.FileInfo().IsDir() && strings.HasSuffix(f.Name, ".txt") {
			rc, err := f.Open()
			if err != nil {
				return fmt.Errorf("failed to open file in zip: %w", err)
			}
			defer rc.Close()

			if _, err := io.Copy(result, rc); err != nil {
				return fmt.Errorf("failed to read file content: %w", err)
			}
			result.WriteString("\n") // Add newline between files
		}
	}
	return nil
}

func isValidZipEntry(name string) bool {
	// Prevent directory traversal attacks
	return !strings.Contains(name, "..") && filepath.Clean(name) == name
}