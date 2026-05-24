package main

import (
	"os"
	"os/exec"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/create-gif", func(c *fiber.Ctx) error {
		// Parse multipart form data
		formData := struct {
			Images        []*fiber.FormFile `form:"images" json:"images"`
			TargetSize    string             `form:"targetSize" json:"targetSize"`
			Delay         int                `form:"delay" json:"delay"`
			AppendReverted bool               `form:"appendReverted" json:"appendReverted"`
		}{}

		formData.Images = c.MultipartForm.File["images"]
		formData.TargetSize = c.FormValue("targetSize")
		if delay, err := strconv.Atoi(c.FormValue("delay")); err == nil {
			formData.Delay = delay
		}
		formData.AppendReverted = c.FormValue("appendReverted") == "true"

		// Validate input
		if len(formData.Images) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "No images provided"})
		}
		if !isValidSize(formData.TargetSize) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid target size format"})
		}
		if formData.Delay < 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Delay must be a non-negative integer"})
		}

		// Prepare temporary files for images
		imageFiles := make([]string, len(formData.Images))
		for i, image := range formData.Images {
			if !isValidImageType(image.Filename) {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Unsupported image type"})
			}
			tempFile, err := os.CreateTemp("", "image-*.png")
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create temp file"})
			}
			if _, err := image.Copy(tempFile); err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to copy image"})
			}
			imageFiles[i] = tempFile.Name()
		}

		// Construct the convert command
		cmdArgs := []string{"-delay", strconv.Itoa(formData.Delay), "-loop", "0"}
		cmdArgs = append(cmdArgs, imageFiles...)
		if formData.AppendReverted {
			cmdArgs = append(cmdArgs, reverseImages(imageFiles)...)
		}
		cmdArgs = append(cmdArgs, "-resize", formData.TargetSize, "output.gif")

		// Execute the command
		cmd := exec.Command("convert", cmdArgs...)
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create GIF"})
		}

		// Clean up temporary files
		defer func() { for _, f := range imageFiles { os.Remove(f) } }()

		// Serve the GIF
		return c.SendFile("output.gif", false)
	})

	app.Listen(":5000")
}

func isValidSize(size string) bool {
	parts := strings.Split(size, "x")
	if len(parts) != 2 {
		return false
	}
	width, err1 := strconv.Atoi(parts[0])
	height, err2 := strconv.Atoi(parts[1])
	return err1 == nil && err2 == nil && width > 0 && height > 0
}

func isValidImageType(filename string) bool {
	allowedExtensions := []string{".jpg", ".jpeg", ".png", ".gif"}
	for _, ext := range allowedExtensions {
		if strings.HasSuffix(strings.ToLower(filename), ext) {
			return true
		}
	}
	return false
}

func reverseImages(images []string) []string {
	reversed := make([]string, len(images))
	for i := len(images) - 1; i >= 0; i-- {
		reversed[len(images)-1-i] = images[i]
	}
	return reversed
}