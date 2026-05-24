package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
)

const uploadDir = "./uploads"

// Allowed file extensions
var allowedExtensions = map[string]bool{
	".jpg":  true,
	".jpeg": true,
	".png":  true,
	".gif":  true,
}

func main() {
	app := fiber.New()

	// Ensure the upload directory exists
	if err := os.MkdirAll(uploadDir, os.ModePerm); err != nil {
		log.Fatalf("Failed to create upload directory: %v", err)
	}

	app.Post("/upload", func(c *fiber.Ctx) error {
		// Parse the multipart form
		fileHeader, err := c.FormFile("file")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		// Validate file extension
		ext := strings.ToLower(filepath.Ext(fileHeader.Filename))
		if !allowedExtensions[ext] {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid file extension"})
		}

		// Generate a unique file name
		fileID := uuid.New().String()
		filePath := filepath.Join(uploadDir, fileID+ext)

		// Save the file
		if err := c.SaveFile(fileHeader, filePath); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save file"})
		}

		return c.JSON(fiber.Map{"id": fileID})
	})

	app.Get("/images/:imageId", func(c *fiber.Ctx) error {
		imageID := c.Params("imageId")

		// Validate imageID to prevent directory traversal
		if strings.Contains(imageID, "..") || strings.Contains(imageID, "/") {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid image ID"})
		}

		// Find the file with the given ID
		var filePath string
		err := filepath.Walk(uploadDir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if strings.HasPrefix(filepath.Base(path), imageID) {
				filePath = path
				return filepath.SkipDir
			}
			return nil
		})

		if err != nil {
			log.Printf("Error walking the path: %v", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}

		if filePath == "" {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Image not found"})
		}

		// Serve the file
		return c.SendFile(filePath)
	})

	// Middleware to set security headers
	app.Use(func(c *fiber.Ctx) error {
		c.Set("Content-Security-Policy", "default-src 'self'")
		c.Set("X-Content-Type-Options", "nosniff")
		c.Set("X-Frame-Options", "DENY")
		c.Set("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
		return c.Next()
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}