package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
)

const maxZipSize = 10 * 1024 * 1024 // 10 MB
const maxFilesInZip = 100

func main() {
	app := fiber.New()

	app.Post("/convert", func(c *fiber.Ctx) error {
		// Validate the content type
		if err := c.Accepts("multipart/form-data"); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Get the file from the form
		file, err := c.FormFile("file")
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Check the file size
		if file.Size > maxZipSize {
			return c.Status(http.StatusBadRequest).SendString("File size exceeds limit")
		}

		// Open the uploaded zip file
		src, err := file.Open()
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}
		defer src.Close()

		// Validate the MIME type
		buf := make([]byte, 512)
		if _, err := src.Read(buf); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}
		if http.DetectContentType(buf) != "application/zip" {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}
		src.Seek(0, 0) // Reset the reader

		// Read the zip file
		zipReader, err := zip.NewReader(src, file.Size)
		if err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Check the number of files in the zip
		if len(zipReader.File) > maxFilesInZip {
			return c.Status(http.StatusBadRequest).SendString("Too many files in zip")
		}

		var buffer bytes.Buffer

		// Iterate through the files in the zip
		for _, zf := range zipReader.File {
			if zf.FileInfo().IsDir() {
				continue
			}

			// Check if the file is a text file
			if zf.FileInfo().Mode().IsRegular() && (zf.Name[len(zf.Name)-4:] == ".txt" || zf.Name[len(zf.Name)-4:] == ".csv") {
				rc, err := zf.Open()
				if err != nil {
					return c.Status(http.StatusBadRequest).SendString("Invalid input")
				}
				defer rc.Close()

				// Read the content of the text file
				_, err = io.Copy(&buffer, rc)
				if err != nil {
					return c.Status(http.StatusBadRequest).SendString("Invalid input")
				}
			}
		}

		// Return the concatenated text
		return c.SendString(buffer.String())
	})

	app.Listen(":5000")
}