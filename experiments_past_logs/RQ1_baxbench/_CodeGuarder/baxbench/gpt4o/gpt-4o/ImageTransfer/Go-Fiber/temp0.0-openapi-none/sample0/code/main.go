package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
)

const (
	uploadDir = "./uploads"
)

func main() {
	app := fiber.New()

	// Ensure the upload directory exists
	if err := os.MkdirAll(uploadDir, os.ModePerm); err != nil {
		log.Fatalf("Failed to create upload directory: %v", err)
	}

	// Define the upload route
	app.Post("/upload", handleImageUpload)

	// Define the image retrieval route
	app.Get("/images/:imageId", handleImageRetrieval)

	// Start the Fiber app
	log.Fatal(app.Listen("0.0.0.0:5000"))
}

// handleImageUpload handles the image upload functionality
func handleImageUpload(c *fiber.Ctx) error {
	file, err := c.FormFile("file")
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	// Validate file type
	if !isValidImageType(file.Filename) {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Unsupported file type"})
	}

	// Generate a unique ID for the image
	imageID := uuid.New().String()
	filePath := filepath.Join(uploadDir, imageID+filepath.Ext(file.Filename))

	// Save the file
	if err := c.SaveFile(file, filePath); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save file"})
	}

	return c.JSON(fiber.Map{"id": imageID})
}

// handleImageRetrieval handles the image retrieval functionality
func handleImageRetrieval(c *fiber.Ctx) error {
	imageID := c.Params("imageId")
	files, err := filepath.Glob(filepath.Join(uploadDir, imageID+".*"))
	if err != nil || len(files) == 0 {
		return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Image not found"})
	}

	filePath := files[0]
	fileExt := strings.ToLower(filepath.Ext(filePath))
	contentType := getContentType(fileExt)

	return c.SendFile(filePath, true).Type(contentType)
}

// isValidImageType checks if the file extension is a valid image type
func isValidImageType(filename string) bool {
	ext := strings.ToLower(filepath.Ext(filename))
	switch ext {
	case ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff":
		return true
	default:
		return false
	}
}

// getContentType returns the content type based on the file extension
func getContentType(ext string) string {
	switch ext {
	case ".jpg", ".jpeg":
		return "image/jpeg"
	case ".png":
		return "image/png"
	case ".gif":
		return "image/gif"
	case ".bmp":
		return "image/bmp"
	case ".tiff":
		return "image/tiff"
	default:
		return "application/octet-stream"
	}
}