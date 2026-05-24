package main

import (
	"archive/zip"
	"bytes"
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
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		// Get the file from the form
		files := form.File["file"]
		if len(files) == 0 {
			return c.Status(fiber.StatusBadRequest).SendString("No file uploaded")
		}

		// Open the uploaded file
		file, err := files[0].Open()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Failed to open file")
		}
		defer file.Close()

		// Process the zip file
		var buffer bytes.Buffer
		if err := processZip(file, &buffer); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Failed to process zip file")
		}

		// Return the concatenated text
		return c.SendString(buffer.String())
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func processZip(file io.Reader, buffer *bytes.Buffer) error {
	zipReader, err := zip.NewReader(file.(io.ReaderAt), fileSize(file))
	if err != nil {
		return fmt.Errorf("failed to read zip file: %w", err)
	}

	for _, file := range zipReader.File {
		if !isValidZipEntry(file) {
			return fmt.Errorf("invalid zip entry: %s", file.Name)
		}

		if filepath.Ext(file.Name) == ".txt" {
			if err := extractAndConcatenate(file, buffer); err != nil {
				return fmt.Errorf("failed to extract file: %w", err)
			}
		}
	}

	return nil
}

func isValidZipEntry(file *zip.File) bool {
	// Prevent Zip Slip vulnerability
	canonicalPath, err := filepath.Abs(file.Name)
	if err != nil {
		return false
	}
	return strings.HasPrefix(canonicalPath, filepath.Clean("/"))
}

func extractAndConcatenate(file *zip.File, buffer *bytes.Buffer) error {
	rc, err := file.Open()
	if err != nil {
		return err
	}
	defer rc.Close()

	_, err = io.Copy(buffer, rc)
	return err
}

func fileSize(file io.Reader) int64 {
	if seeker, ok := file.(io.Seeker); ok {
		currentPos, _ := seeker.Seek(0, io.SeekCurrent)
		endPos, _ := seeker.Seek(0, io.SeekEnd)
		seeker.Seek(currentPos, io.SeekStart)
		return endPos
	}
	return 0
}