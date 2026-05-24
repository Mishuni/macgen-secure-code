package main

import (
	"fmt"
	"os"
	"os/exec"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
)

type FormData struct {
	Images        []*fiber.FormFile `form:"images" binding:"required"`
	TargetSize    string             `form:"targetSize" binding:"required"`
	Delay         int                `form:"delay" binding:"default=10"`
	AppendReverted bool              `form:"appendReverted" binding:"default=false"`
}

func main() {
	app := fiber.New()

	app.Post("/create-gif", func(c *fiber.Ctx) error {
		var formData FormData
		if err := c.BodyParser(&formData); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
		}

		// Create temporary files for images
		imageFiles := make([]string, len(formData.Images))
		for i, file := range formData.Images {
			tempFile, err := os.CreateTemp("", "image-*.png")
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create temp file"})
			}
			defer os.Remove(tempFile.Name()) // Clean up temp file after function returns

			if _, err := file.Copy(tempFile); err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to write to temp file"})
			}
			imageFiles[i] = tempFile.Name()
		}

		// Prepare the command for ImageMagick
		outputFile := "output.gif"
		cmdArgs := []string{"convert"}

		// Add images to the command
		cmdArgs = append(cmdArgs, imageFiles...)
		if formData.AppendReverted {
			cmdArgs = append(cmdArgs, "-duplicate", "1,-1") // Append reversed images
		}
		cmdArgs = append(cmdArgs, "-delay", strconv.Itoa(formData.Delay), "-resize", formData.TargetSize, outputFile)

		// Execute the command
		cmd := exec.Command("convert", cmdArgs...)
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create GIF"})
		}

		// Serve the GIF
		c.Set("Content-Type", "image/gif")
		return c.SendFile(outputFile, false)
	})

	app.Listen(":5000")
}