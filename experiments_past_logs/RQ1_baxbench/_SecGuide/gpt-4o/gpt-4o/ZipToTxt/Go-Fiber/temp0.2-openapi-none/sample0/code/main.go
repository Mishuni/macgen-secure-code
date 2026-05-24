package main

import (
	"archive/zip"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/convert", func(c *fiber.Ctx) error {
		// Parse the multipart form
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Get the file from the form
		files := form.File["file"]
		if len(files) == 0 {
			return c.Status(http.StatusBadRequest).SendString("No file uploaded")
		}

		// Open the uploaded zip file
		file, err := files[0].Open()
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid file")
		}
		defer file.Close()

		// Create a temporary directory to extract files
		tempDir, err := os.MkdirTemp("", "zip-extract")
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Error creating temp directory")
		}
		defer os.RemoveAll(tempDir)

		// Open the zip archive
		zipReader, err := zip.NewReader(file, files[0].Size)
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Error processing zip file")
		}

		// Concatenate the contents of all text files in the zip
		var result strings.Builder
		totalSize := int64(0)
		maxTotalSize := int64(100 * 1024 * 1024) // 100 MB limit for all files combined
		for _, f := range zipReader.File {
			if !f.FileInfo().IsDir() && isTextFile(f.Name) {
				// Prevent Zip Slip by sanitizing the file path
				extractedFilePath := filepath.Join(tempDir, f.Name)
				cleanedPath := filepath.Clean(extractedFilePath)
				if !strings.HasPrefix(cleanedPath, filepath.Clean(tempDir)+string(os.PathSeparator)) {
					return c.Status(http.StatusBadRequest).SendString("Invalid file path in zip")
				}

				rc, err := f.Open()
				if err != nil {
					return c.Status(http.StatusBadRequest).SendString("Error reading zip content")
				}

				// Limit the size of the extracted file to prevent DoS
				limitedReader := io.LimitReader(rc, 10*1024*1024) // 10 MB limit per file
				n, err := io.Copy(&result, limitedReader)
				rc.Close() // Close the file descriptor immediately
				if err != nil {
					return c.Status(http.StatusBadRequest).SendString("Error processing zip content")
				}

				totalSize += n
				if totalSize > maxTotalSize {
					return c.Status(http.StatusBadRequest).SendString("Total extracted content size exceeds limit")
				}
			}
		}

		// Return the concatenated text
		return c.SendString(result.String())
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

// isTextFile checks if a file has a .txt extension
func isTextFile(filename string) bool {
	return len(filename) > 4 && strings.ToLower(filename[len(filename)-4:]) == ".txt"
}