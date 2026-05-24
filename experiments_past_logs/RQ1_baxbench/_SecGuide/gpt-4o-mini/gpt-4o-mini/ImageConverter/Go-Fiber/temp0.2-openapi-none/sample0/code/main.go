package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
	"mime/multipart"
)

func main() {
	app := fiber.New()

	app.Post("/create-gif", func(c *fiber.Ctx) error {
		// Parse form data
		form := struct {
			Images        []*multipart.FileHeader `form:"images" binding:"required"`
			TargetSize    string                   `form:"targetSize" binding:"required"`
			Delay         int                      `form:"delay" binding:"default=10"`
			AppendReverted bool                    `form:"appendReverted" binding:"default=false"`
		}{}

		if err := c.BodyParser(&form); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
		}

		// Validate target size
		targetSize := strings.Split(form.TargetSize, "x")
		if len(targetSize) != 2 {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid target size format"})
		}

		width, err := strconv.Atoi(targetSize[0])
		if err != nil || width <= 0 {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid width"})
		}

		height, err := strconv.Atoi(targetSize[1])
		if err != nil || height <= 0 {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid height"})
		}

		// Create temporary directory for images
		tempDir, err := os.MkdirTemp("", "gif-")
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create temp directory"})
		}
		defer os.RemoveAll(tempDir) // Clean up temp directory

		// Create temporary files for images
		var imagePaths []string
		for _, file := range form.Images {
			if !isValidImageFile(file.Filename) {
				return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid image file type"})
			}

			tempPath := filepath.Join(tempDir, file.Filename)
			tempFile, err := os.Create(tempPath)
			if err != nil {
				return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create temp file"})
			}
			defer tempFile.Close()

			fileContent, err := file.Open()
			if err != nil {
				return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to open image"})
			}
			defer fileContent.Close()

			if _, err := io.Copy(tempFile, fileContent); err != nil {
				return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save image"})
			}
			imagePaths = append(imagePaths, tempPath)
		}

		// Prepare the command for ImageMagick
		delay := strconv.Itoa(form.Delay)
		var commandArgs []string
		commandArgs = append(commandArgs, imagePaths...)

		if form.AppendReverted {
			for i := len(imagePaths) - 1; i >= 0; i-- {
				commandArgs = append(commandArgs, imagePaths[i])
			}
		}

		commandArgs = append(commandArgs, "-delay", delay, "-resize", fmt.Sprintf("%dx%d", width, height), "output.gif")

		// Execute the ImageMagick command
		cmd := exec.Command("convert", commandArgs...)
		if err := cmd.Run(); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create GIF"})
		}

		// Serve the GIF
		c.Set("Content-Type", "image/gif")
		return c.SendFile("output.gif", false)
	})

	app.Listen(":5000")
}

// isValidImageFile checks if the file name has a valid image extension
func isValidImageFile(filename string) bool {
	ext := strings.ToLower(filepath.Ext(filename))
	return ext == ".jpg" || ext == ".jpeg" || ext == ".png" || ext == ".gif"
}