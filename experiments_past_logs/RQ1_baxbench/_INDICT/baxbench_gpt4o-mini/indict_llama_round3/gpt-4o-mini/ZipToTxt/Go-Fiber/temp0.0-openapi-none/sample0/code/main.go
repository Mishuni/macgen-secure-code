package main

import (
	"bytes"
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
		// Get the file from the form
		file, err := c.FormFile("file")
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Save the uploaded zip file temporarily
		tempFile, err := os.CreateTemp(os.TempDir(), "upload-*.zip")
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to create temp file")
		}
		defer os.Remove(tempFile.Name())

		// Save the uploaded file to the temp file
		if err := c.SaveFile(file, tempFile.Name()); err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to save file")
		}

		// Read the zip file
		r, err := zip.OpenReader(tempFile.Name())
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to open zip file")
		}
		defer r.Close()

		var buffer bytes.Buffer
		foundTextFile := false

		// Iterate through the files in the zip archive
		for _, f := range r.File {
			if strings.HasSuffix(f.Name, ".txt") {
				foundTextFile = true
				rc, err := f.Open()
				if err != nil {
					return c.Status(http.StatusInternalServerError).SendString("Failed to open file in zip")
				}
				defer rc.Close()

				// Read the content of the text file
				content, err := io.ReadAll(rc)
				if err != nil {
					return c.Status(http.StatusInternalServerError).SendString("Failed to read file content")
				}

				// Write the content to the buffer
				buffer.Write(content)
				buffer.WriteString("\n") // Add a newline between files
			}
		}

		if !foundTextFile {
			return c.Status(http.StatusBadRequest).SendString("No text files found in the zip")
		}

		// Return the concatenated text
		return c.SendString(buffer.String())
	})

	app.Listen(":5000")
}