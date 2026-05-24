package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/create-gif", func(c *fiber.Ctx) error {
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid form data"})
		}

		images := form.File["images"]
		if len(images) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "No images provided"})
		}

		targetSize := c.FormValue("targetSize")
		if !isValidTargetSize(targetSize) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid target size format"})
		}

		delayStr := c.FormValue("delay", "10")
		delay, err := strconv.Atoi(delayStr)
		if err != nil || delay < 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid delay value"})
		}

		appendReverted := c.FormValue("appendReverted", "false") == "true"

		tempDir, err := os.MkdirTemp("", "gifcreator")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create temp directory"})
		}
		defer os.RemoveAll(tempDir)

		var imagePaths []string
		for _, fileHeader := range images {
			file, err := fileHeader.Open()
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to open image"})
			}
			defer file.Close()

			imagePath := filepath.Join(tempDir, fileHeader.Filename)
			outFile, err := os.Create(imagePath)
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save image"})
			}
			defer outFile.Close()

			_, err = outFile.ReadFrom(file)
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to read image"})
			}

			imagePaths = append(imagePaths, imagePath)
		}

		gifPath := filepath.Join(tempDir, "output.gif")
		cmdArgs := []string{"-delay", strconv.Itoa(delay), "-resize", targetSize}
		cmdArgs = append(cmdArgs, imagePaths...)
		if appendReverted {
			for i := len(imagePaths) - 1; i >= 0; i-- {
				cmdArgs = append(cmdArgs, imagePaths[i])
			}
		}
		cmdArgs = append(cmdArgs, gifPath)

		cmd := exec.Command("convert", cmdArgs...)
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create GIF"})
		}

		gifFile, err := os.Open(gifPath)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to open GIF"})
		}
		defer gifFile.Close()

		c.Set("Content-Type", "image/gif")
		return c.SendStream(gifFile)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func isValidTargetSize(size string) bool {
	re := regexp.MustCompile(`^\d+x\d+$`)
	return re.MatchString(size)
}