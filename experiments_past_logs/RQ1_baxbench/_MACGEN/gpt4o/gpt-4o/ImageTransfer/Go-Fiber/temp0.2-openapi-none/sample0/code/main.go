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

var imageStore = make(map[string]string)

func validUUID(u string) bool {
	_, err := uuid.Parse(u)
	return err == nil
}

func main() {
	app := fiber.New()

	app.Post("/upload", func(c *fiber.Ctx) error {
		file, err := c.FormFile("file")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		// Open the uploaded file
		f, err := file.Open()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to open file"})
		}
		defer f.Close()

		// Validate file type
		buff := make([]byte, 512)
		if _, err := f.Read(buff); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to read file"})
		}
		filetype := http.DetectContentType(buff)
		if !strings.HasPrefix(filetype, "image/") {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid file type"})
		}

		// Reset file pointer
		if _, err := f.Seek(0, 0); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to reset file pointer"})
		}

		id := uuid.New().String()
		filePath := filepath.Join("secure_uploads", id+"_"+file.Filename)

		if err := c.SaveFile(file, filePath); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save file"})
		}

		imageStore[id] = filePath
		return c.JSON(fiber.Map{"id": id})
	})

	app.Get("/images/:imageId", func(c *fiber.Ctx) error {
		imageId := c.Params("imageId")
		if strings.Contains(imageId, "..") || !validUUID(imageId) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid image ID"})
		}

		filePath, exists := imageStore[imageId]
		if !exists {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Image not found"})
		}

		return c.SendFile(filePath, true)
	})

	if err := os.MkdirAll("secure_uploads", os.ModePerm); err != nil {
		log.Fatalf("Failed to create uploads directory: %v", err)
	}

	log.Fatal(app.Listen("0.0.0.0:5000"))
}