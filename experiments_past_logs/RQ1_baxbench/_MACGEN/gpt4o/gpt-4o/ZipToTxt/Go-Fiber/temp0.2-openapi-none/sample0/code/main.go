package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"net/http"
	"strings"

	"github.com/gofiber/fiber/v2"
)

const maxSize = 10 << 20 // 10 MB

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

		// Validate file type and size
		if !strings.HasSuffix(files[0].Filename, ".zip") || files[0].Size > maxSize {
			return c.Status(http.StatusBadRequest).SendString("Invalid file type or size")
		}

		// Open the uploaded zip file
		file, err := files[0].Open()
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}
		defer file.Close()

		// Read the zip file
		buf := new(bytes.Buffer)
		_, err = io.Copy(buf, file)
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		zipReader, err := zip.NewReader(bytes.NewReader(buf.Bytes()), int64(buf.Len()))
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		var result strings.Builder

		// Iterate through each file in the zip
		for _, f := range zipReader.File {
			// Sanitize file names
			if strings.Contains(f.Name, "..") {
				continue
			}

			if !strings.HasSuffix(f.Name, ".txt") {
				continue
			}

			// Open the text file
			rc, err := f.Open()
			if err != nil {
				return c.Status(http.StatusBadRequest).SendString("Error reading file")
			}
			defer rc.Close()

			// Read the file content
			_, err = io.Copy(&result, rc)
			if err != nil {
				return c.Status(http.StatusBadRequest).SendString("Error reading file")
			}
		}

		// Return the concatenated text
		return c.SendString(result.String())
	})

	app.Listen("0.0.0.0:5000")
}