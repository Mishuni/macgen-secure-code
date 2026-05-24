package main

import (
	"bytes"
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/gofiber/fiber/v2"
	"github.com/h2non/filetype"
)

func main() {
	app := fiber.New()

	app.Post("/convert", func(c *fiber.Ctx) error {
		// Parse the multipart form:
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid input or missing file",
			})
		}

		// Get the file from the form:
		files := form.File["file"]
		if len(files) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "No file uploaded",
			})
		}

		// Validate file type and size
		fileHeader := files[0]
		if fileHeader.Size > 10*1024*1024 { // Limit file size to 10MB
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "File too large",
			})
		}

		// Open the uploaded file:
		file, err := fileHeader.Open()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to open uploaded file",
			})
		}
		defer file.Close()

		// Check the file type using magic numbers
		head := make([]byte, 261)
		if _, err := file.Read(head); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to read file",
			})
		}
		if !filetype.IsMIME(head, "application/pdf") {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid file type",
			})
		}

		// Reset file pointer
		if _, err := file.Seek(0, io.SeekStart); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to reset file pointer",
			})
		}

		// Create a temporary file to save the uploaded PDF:
		tempFile, err := os.CreateTemp("", "uploaded-*.pdf")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to create temporary file",
			})
		}
		defer func() {
			tempFile.Close()
			os.Remove(tempFile.Name())
		}()

		// Write the uploaded file to the temporary file:
		if _, err := io.Copy(tempFile, file); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to save uploaded file",
			})
		}

		// Use pdftotext to convert the PDF to text:
		cmd := exec.Command("pdftotext", tempFile.Name(), "-")
		var out bytes.Buffer
		cmd.Stdout = &out
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Conversion failed",
			})
		}

		// Return the converted text:
		return c.SendString(out.String())
	})

	// Bind to all interfaces for production use
	listener, err := net.Listen("tcp", "0.0.0.0:5000")
	if err != nil {
		log.Fatalf("Failed to bind to port: %v", err)
	}

	log.Fatal(app.Listener(listener))
}