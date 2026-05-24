package main

import (
	"fmt"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
)

const uploadDir = "./uploads"

func main() {
	app := fiber.New()

	if err := os.MkdirAll(uploadDir, os.ModePerm); err != nil {
		panic(err)
	}

	app.Post("/upload", uploadImage)
	app.Get("/images/:imageId", shareImage)

	app.Listen(":5000")
}

func uploadImage(c *fiber.Ctx) error {
	file, err := c.FormFile("file")
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
	}

	if err := validateFile(file); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": err.Error()})
	}

	imageID := uuid.New().String()
	filePath := filepath.Join(uploadDir, sanitizeFileName(imageID+filepath.Ext(file.Filename)))

	if err := c.SaveFile(file, filePath); err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save file"})
	}

	return c.JSON(fiber.Map{"id": imageID})
}

func shareImage(c *fiber.Ctx) error {
	imageID := c.Params("imageId")
	filePath := filepath.Join(uploadDir, imageID)

	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Image not found"})
	}

	return c.SendFile(filePath, false)
}

func validateFile(file *multipart.FileHeader) error {
	allowedTypes := map[string]bool{
		"image/jpeg": true,
		"image/png":  true,
		"image/gif":  true,
	}

	buff := make([]byte, 512)
	f, err := file.Open()
	if err != nil {
		return fmt.Errorf("failed to open file")
	}
	defer f.Close()

	if _, err := f.Read(buff); err != nil {
		return fmt.Errorf("failed to read file")
	}
	if err := f.Seek(0, 0); err != nil {
		return fmt.Errorf("failed to seek file")
	}

	if !allowedTypes[http.DetectContentType(buff)] {
		return fmt.Errorf("unsupported file type")
	}
	return nil
}

func sanitizeFileName(fileName string) string {
	return strings.ReplaceAll(fileName, "..", "")
}