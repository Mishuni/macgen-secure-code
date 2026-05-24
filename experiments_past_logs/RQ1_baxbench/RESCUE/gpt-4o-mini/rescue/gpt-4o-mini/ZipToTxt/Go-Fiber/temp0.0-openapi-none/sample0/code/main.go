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

		// Validate file type
		if !strings.HasSuffix(file.Filename, ".zip") {
			return c.Status(http.StatusBadRequest).SendString("Invalid file type, must be a zip file")
		}

		// Save the uploaded zip file temporarily
		tempFilePath := filepath.Join(os.TempDir(), file.Filename)
		if err := c.SaveFile(file, tempFilePath); err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to save file")
		}
		defer os.Remove(tempFilePath) // Clean up the temp file

		// Open the zip file
		zipReader, err := zip.OpenReader(tempFilePath)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to open zip file")
		}
		defer zipReader.Close()

		var buffer bytes.Buffer

		// Read each file in the zip
		for _, zf := range zipReader.File {
			if strings.HasSuffix(zf.Name, ".txt") {
				// Open the text file
				fileReader, err := zf.Open()
				if err != nil {
					return c.Status(http.StatusInternalServerError).SendString("Failed to open file in zip")
				}
				defer fileReader.Close()

				// Copy the contents to the buffer
				if _, err := io.Copy(&buffer, fileReader); err != nil {
					return c.Status(http.StatusInternalServerError).SendString("Failed to read file in zip")
				}
			}
		}

		// Return the concatenated text
		return c.SendString(buffer.String())
	})

	app.Listen(":5000")
}