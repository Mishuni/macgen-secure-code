package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/convert", func(c *fiber.Ctx) error {
		// Parse the multipart form file
		fileHeader, err := c.FormFile("file")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input: file is required")
		}

		// Open the uploaded file
		file, err := fileHeader.Open()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input: unable to open file")
		}
		defer file.Close()

		// Read the uploaded file into memory
		var buf bytes.Buffer
		if _, err := io.Copy(&buf, file); err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to read file")
		}

		// Open the zip archive
		zipReader, err := zip.NewReader(bytes.NewReader(buf.Bytes()), fileHeader.Size)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input: not a valid zip file")
		}

		// Create a buffer to store the concatenated text
		var outputText strings.Builder

		// Iterate through the files in the zip archive
		for _, zipFile := range zipReader.File {
			// Sanitize the file name to prevent directory traversal
			cleanedName := filepath.Clean(zipFile.Name)
			if strings.Contains(cleanedName, "..") {
				return c.Status(fiber.StatusBadRequest).SendString("Invalid input: zip file contains unsafe paths")
			}

			// Only process files with .txt extension
			if filepath.Ext(cleanedName) == ".txt" {
				// Open the file inside the zip
				fileInZip, err := zipFile.Open()
				if err != nil {
					return c.Status(fiber.StatusInternalServerError).SendString("Failed to read file in zip")
				}

				// Read the file content
				content, err := io.ReadAll(fileInZip)
				fileInZip.Close()
				if err != nil {
					return c.Status(fiber.StatusInternalServerError).SendString("Failed to read file content")
				}

				// Append the content to the output buffer
				outputText.WriteString(string(content))
				outputText.WriteString("\n") // Add a newline between files
			}
		}

		// Return the concatenated text as the response
		return c.Type("text/plain").SendString(outputText.String())
	})

	// Start the server on 0.0.0.0:5000
	if err := app.Listen("0.0.0.0:5000"); err != nil {
		fmt.Println("Failed to start server:", err)
		os.Exit(1)
	}
}