package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
)

const storageDir = "./uploads/"

func main() {
	app := fiber.New()

	// Create the uploads directory if it doesn't exist
	if err := os.MkdirAll(storageDir, os.ModePerm); err != nil {
		fmt.Println("Error creating uploads directory:", err)
		return
	}

	app.Post("/upload", uploadImage)
	app.Get("/images/:imageId", shareImage)

	app.Listen(":5000")
}

func uploadImage(c *fiber.Ctx) error {
	// Parse the multipart form
	if err := c.BodyParser(&fiber.Map{}); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	file, err := c.FormFile("file")
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "File is required"})
	}

	// Sanitize the file name
	fileName := sanitizeFileName(file.Filename)
	newFilePath := filepath.Join(storageDir, fileName)

	// Save the file
	if err := c.SaveFile(file, newFilePath); err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save file"})
	}

	// Generate a shareable ID
	imageID := uuid.New().String()

	return c.JSON(fiber.Map{"id": imageID})
}

func shareImage(c *fiber.Ctx) error {
	imageID := c.Params("imageId")
	imagePath := filepath.Join(storageDir, imageID)

	// Check if the file exists
	if _, err := os.Stat(imagePath); os.IsNotExist(err) {
		return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Image not found"})
	}

	// Serve the image
	return c.SendFile(imagePath, false)
}

func sanitizeFileName(fileName string) string {
	// Sanitize the file name to prevent directory traversal
	return filepath.Base(fileName)
}