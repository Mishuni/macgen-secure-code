package main

import (
	"bytes"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"archive/zip"

	"github.com/gofiber/fiber/v2"
)

const maxUploadSize = 10 * 1024 * 1024 // 10 MB
const maxUncompressedSize = 5 * 1024 * 1024 // 5 MB

func main() {
	app := fiber.New()

	app.Post("/convert", func(c *fiber.Ctx) error {
		// Parse the multipart form
		err := c.Accepts("multipart/form-data")
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Get the file from the form
		file, err := c.FormFile("file")
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Check file size
		if file.Size > maxUploadSize {
			return c.Status(http.StatusBadRequest).SendString("File too large")
		}

		// Open the zip file
		src, err := file.Open()
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}
		defer src.Close()

		// Validate the zip file content
		if !isValidZipFile(src) {
			return c.Status(http.StatusBadRequest).SendString("Invalid zip file")
		}

		// Reset the reader to read the zip file again
		src.Seek(0, 0)

		// Read the zip file
		zipReader, err := zip.NewReader(src, file.Size)
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		var buffer bytes.Buffer
		var totalUncompressedSize int64

		// Iterate through the files in the zip archive
		for _, zf := range zipReader.File {
			// Sanitize file name to prevent path traversal
			if !isValidFileName(zf.Name) {
				return c.Status(http.StatusBadRequest).SendString("Invalid file name in zip")
			}

			if strings.HasSuffix(zf.Name, ".txt") {
				// Open the text file
				rc, err := zf.Open()
				if err != nil {
					return c.Status(http.StatusInternalServerError).SendString("Error reading zip file")
				}

				// Check uncompressed size
				if totalUncompressedSize+int64(zf.UncompressedSize64) > maxUncompressedSize {
					rc.Close()
					return c.Status(http.StatusBadRequest).SendString("Uncompressed size exceeds limit")
				}
				totalUncompressedSize += int64(zf.UncompressedSize64)

				// Read the content of the text file
				_, err = io.Copy(&buffer, rc)
				rc.Close() // Close immediately after use
				if err != nil {
					return c.Status(http.StatusInternalServerError).SendString("Error reading zip file")
				}
				buffer.WriteString("\n") // Add a newline between files
			}
		}

		// Return the concatenated text with proper encoding
		return c.SendString(escapeHTML(buffer.String()))
	})

	app.Listen(":5000")
}

// isValidZipFile checks if the file is a valid zip file by checking its magic number
func isValidZipFile(file io.Reader) bool {
	header := make([]byte, 4)
	_, err := file.Read(header)
	if err != nil {
		return false
	}
	// Check for the ZIP file signature
	return header[0] == 'P' && header[1] == 'K' && header[2] == 0x03 && header[3] == 0x04
}

// isValidFileName checks for path traversal and invalid characters in file names
func isValidFileName(name string) bool {
	// Check for invalid characters and patterns
	if strings.Contains(name, "..") || strings.Contains(name, "/") || strings.Contains(name, "\\") {
		return false
	}
	return true
}

// escapeHTML escapes special HTML characters to prevent XSS
func escapeHTML(input string) string {
	return strings.ReplaceAll(strings.ReplaceAll(strings.ReplaceAll(input, "&", "&amp;"), "<", "&lt;"), ">", "&gt;")
}