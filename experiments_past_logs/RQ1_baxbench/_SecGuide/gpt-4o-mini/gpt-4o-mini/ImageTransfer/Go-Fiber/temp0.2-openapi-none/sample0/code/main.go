package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
)

const uploadDir = "./uploads"
const maxFileSize = 5 * 1024 * 1024 // 5 MB

// Allowed file extensions
var allowedExtensions = map[string]bool{
	".jpg":  true,
	".jpeg": true,
	".png":  true,
	".gif":  true,
}

func main() {
	app := fiber.New()

	// Create upload directory if it doesn't exist with restrictive permissions
	if err := os.MkdirAll(uploadDir, 0700); err != nil {
		fmt.Println("Error creating upload directory:", err)
		return
	}

	app.Post("/upload", func(c *fiber.Ctx) error {
		// Parse the multipart form
		if err := c.BodyParser(&fiber.FormData{}); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		file, err := c.FormFile("file")
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "File is required"})
		}

		// Validate file size
		if file.Size > maxFileSize {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "File is too large"})
		}

		// Validate file type
		ext := strings.ToLower(filepath.Ext(file.Filename))
		if !allowedExtensions[ext] {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid file type"})
		}

		// Sanitize filename and prevent directory traversal
		sanitizedFilename := filepath.Base(file.Filename)
		if strings.Contains(sanitizedFilename, "..") || strings.Contains(sanitizedFilename, "/") {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid file name"})
		}

		// Generate a unique file path
		imageID := uuid.New().String()
		filePath := filepath.Join(uploadDir, imageID+ext)

		// Save the file
		if err := c.SaveFile(file, filePath); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save file"})
		}

		return c.JSON(fiber.Map{"id": imageID})
	})

	app.Get("/images/:imageId", func(c *fiber.Ctx) error {
		imageID := c.Params("imageId")
		imagePath := filepath.Join(uploadDir, imageID)

		// Check if the file exists
		if _, err := os.Stat(imagePath); os.IsNotExist(err) {
			return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Image not found"})
		}

		// Serve the image with appropriate headers
		return c.SendFile(imagePath, false)
	})

	app.Listen(":5000")
}