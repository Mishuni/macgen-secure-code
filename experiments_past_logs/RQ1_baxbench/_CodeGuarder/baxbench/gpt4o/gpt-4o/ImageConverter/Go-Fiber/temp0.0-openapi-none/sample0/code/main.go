package main

import (
	"bytes"
	"fmt"
	"image"
	"image/gif"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/create-gif", func(c *fiber.Ctx) error {
		// Parse and validate request data
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid form data"})
		}

		images := form.File["images"]
		if len(images) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "No images provided"})
		}

		targetSize := c.FormValue("targetSize")
		if targetSize == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Target size is required"})
		}

		delayStr := c.FormValue("delay", "10")
		delay, err := strconv.Atoi(delayStr)
		if err != nil || delay < 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid delay value"})
		}

		appendReverted := c.FormValue("appendReverted", "false") == "true"

		// Process images and create GIF
		var imagePaths []string
		for _, fileHeader := range images {
			file, err := fileHeader.Open()
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to open image"})
			}
			defer file.Close()

			tempFile, err := os.CreateTemp("", "image-*.png")
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create temp file"})
			}
			defer os.Remove(tempFile.Name())

			if _, err := io.Copy(tempFile, file); err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save image"})
			}
			imagePaths = append(imagePaths, tempFile.Name())
		}

		gifPath, err := createGIF(imagePaths, targetSize, delay, appendReverted)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
		}
		defer os.Remove(gifPath)

		// Send the GIF as response
		c.Set("Content-Type", "image/gif")
		return c.SendFile(gifPath)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createGIF(imagePaths []string, targetSize string, delay int, appendReverted bool) (string, error) {
	args := []string{"-delay", strconv.Itoa(delay), "-resize", targetSize}
	args = append(args, imagePaths...)

	if appendReverted {
		for i := len(imagePaths) - 1; i >= 0; i-- {
			args = append(args, imagePaths[i])
		}
	}

	tempGIF, err := os.CreateTemp("", "output-*.gif")
	if err != nil {
		return "", fmt.Errorf("failed to create temp GIF file")
	}
	defer tempGIF.Close()

	args = append(args, tempGIF.Name())

	cmd := exec.Command("convert", args...)
	var stderr bytes.Buffer
	cmd.Stderr = &stderr

	if err := cmd.Run(); err != nil {
		return "", fmt.Errorf("failed to create GIF: %s", stderr.String())
	}

	return tempGIF.Name(), nil
}