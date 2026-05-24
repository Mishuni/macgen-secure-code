package main

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/h2non/filetype"
)

const imageDir = "./images"

func main() {
	app := fiber.New()

	// Create images directory if it doesn't exist
	os.MkdirAll(imageDir, os.ModePerm)

	app.Post("/upload", uploadImage)
	app.Get("/images/:imageId", shareImage)

	app.Listen(":5000")
}

func uploadImage(c *fiber.Ctx) error {
	// Parse the multipart form
	file, err := c.FormFile("file")
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "File is required"})
	}

	// Validate file type
	if err := validateFileType(file); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": err.Error()})
	}

	// Generate a unique ID for the image
	imageID := uuid.New().String()
	imagePath := filepath.Join(imageDir, imageID+filepath.Ext(file.Filename))

	// Save the file
	if err := c.SaveFile(file, imagePath); err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save image"})
	}

	return c.JSON(fiber.Map{"id": imageID})
}

func shareImage(c *fiber.Ctx) error {
	imageID := c.Params("imageId")
	imagePath := filepath.Join(imageDir, imageID)

	// Check if the image exists
	if _, err := os.Stat(imagePath); os.IsNotExist(err) {
		return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Image not found"})
	}

	// Serve the image with the original MIME type
	return c.SendFile(imagePath, false)
}

func validateFileType(file *fiber.FormFile) error {
	// Read the file header to determine the file type
	f, err := file.Open()
	if err != nil {
		return fmt.Errorf("unable to open file")
	}
	defer f.Close()

	buf := make([]byte, 512)
	if _, err := f.Read(buf); err != nil {
		return fmt.Errorf("unable to read file")
	}

	// Check the file type
	if kind, _ := filetype.Match(buf); kind == filetype.Unknown {
		return fmt.Errorf("invalid file type")
	}

	return nil
}