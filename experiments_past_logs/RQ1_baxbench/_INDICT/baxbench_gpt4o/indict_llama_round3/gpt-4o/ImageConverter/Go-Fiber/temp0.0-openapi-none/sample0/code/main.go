package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"strconv"
	"strings"

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
		if targetSize == "" || !isValidSize(targetSize) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid target size"})
		}

		delayStr := c.FormValue("delay", "10")
		delay, err := strconv.Atoi(delayStr)
		if err != nil || delay < 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid delay value"})
		}

		appendReverted := c.FormValue("appendReverted", "false") == "true"

		tempDir, err := os.MkdirTemp("", "gifcreator")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create temporary directory"})
		}
		defer os.RemoveAll(tempDir)

		var imagePaths []string
		for _, fileHeader := range images {
			file, err := fileHeader.Open()
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to open image file"})
			}
			defer file.Close()

			imagePath := fmt.Sprintf("%s/%s", tempDir, fileHeader.Filename)
			outFile, err := os.Create(imagePath)
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create image file"})
			}
			defer outFile.Close()

			_, err = outFile.ReadFrom(file)
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save image file"})
			}

			imagePaths = append(imagePaths, imagePath)
		}

		if appendReverted {
			for i := len(imagePaths) - 1; i >= 0; i-- {
				imagePaths = append(imagePaths, imagePaths[i])
			}
		}

		outputGif := fmt.Sprintf("%s/output.gif", tempDir)
		args := append([]string{"-delay", strconv.Itoa(delay), "-resize", targetSize}, imagePaths...)
		args = append(args, outputGif)

		cmd := exec.Command("convert", args...)
		err = cmd.Run()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create GIF"})
		}

		return c.SendFile(outputGif)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
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