package main

import (
	"fmt"
	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"io"
	"net/http"
	"os"
	"path/filepath"
)

func main() {
	app := fiber.New()

	// Create a directory to store uploaded images
	if err := os.MkdirAll("./uploads", os.ModePerm); err != nil {
		panic(err)
	}

	app.Post("/upload", func(c *fiber.Ctx) error {
		// Parse the multipart form:
		file, err := c.FormFile("file")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		// Generate a unique ID for the image
		imageID := uuid.New().String()
		fileExt := filepath.Ext(file.Filename)
		if fileExt == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "File must have an extension"})
		}
		filePath := filepath.Join("./uploads", imageID+fileExt)

		// Save the file to the server
		if err := c.SaveFile(file, filePath); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Could not save file"})
		}

		// Return the image ID
		return c.JSON(fiber.Map{"id": imageID})
	})

	app.Get("/images/:imageId", func(c *fiber.Ctx) error {
		imageID := c.Params("imageId")
		files, err := filepath.Glob("./uploads/" + imageID + ".*")
		if err != nil || len(files) == 0 {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Image not found"})
		}

		// Open the image file
		file, err := os.Open(files[0])
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Could not open file"})
		}
		defer file.Close()

		// Get the file's content type
		buffer := make([]byte, 512)
		if _, err := file.Read(buffer); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Could not read file"})
		}
		contentType := http.DetectContentType(buffer)

		// Reset the file pointer
		if _, err := file.Seek(0, io.SeekStart); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Could not reset file pointer"})
		}

		// Stream the file to the client
		c.Set("Content-Type", contentType)
		return c.SendStream(file)
	})

	// Start the server
	if err := app.Listen("0.0.0.0:5000"); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}