package main

import (
	"archive/zip"
	"bytes"
	"io"
	"log"
	"net/http"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New(fiber.Config{
		BodyLimit: 10 * 1024 * 1024, // Limit upload size to 10 MB
	})

	app.Post("/convert", func(c *fiber.Ctx) error {
		// Parse the multipart form:
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Get the file from the form:
		files := form.File["file"]
		if len(files) == 0 {
			return c.Status(http.StatusBadRequest).SendString("No file uploaded")
		}

		// Open the uploaded zip file:
		file, err := files[0].Open()
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}
		defer file.Close()

		// Read the zip file:
		buf := new(bytes.Buffer)
		_, err = io.Copy(buf, file)
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Open the zip archive:
		zipReader, err := zip.NewReader(bytes.NewReader(buf.Bytes()), int64(buf.Len()))
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Concatenate the contents of all text files:
		var result bytes.Buffer
		for _, f := range zipReader.File {
			if !f.FileInfo().IsDir() {
				// Check if the file is a text file by extension:
				if strings.ToLower(filepath.Ext(f.Name)) == ".txt" {
					rc, err := f.Open()
					if err != nil {
						return c.Status(http.StatusBadRequest).SendString("Invalid input")
					}
					defer rc.Close()

					_, err = io.Copy(&result, rc)
					if err != nil {
						return c.Status(http.StatusBadRequest).SendString("Invalid input")
					}
				}
			}
		}

		// Return the concatenated text:
		return c.SendString(result.String())
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}