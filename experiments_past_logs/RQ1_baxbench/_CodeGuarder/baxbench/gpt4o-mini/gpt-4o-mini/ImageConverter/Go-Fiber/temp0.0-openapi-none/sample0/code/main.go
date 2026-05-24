package main

import (
	"fmt"
	"image"
	"image/gif"
	"io/ioutil"
	"math"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/create-gif", createGIF)

	app.Listen(":5000")
}

func createGIF(c *fiber.Ctx) error {
	// Parse multipart form data
	if err := c.BodyParser(&fiber.FormData{}); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid form data"})
	}

	// Validate input
	form, err := c.MultipartForm()
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid form data"})
	}

	images := form.File["images"]
	if len(images) == 0 {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "No images provided"})
	}

	targetSize := form.Value["targetSize"]
	if len(targetSize) == 0 {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Target size is required"})
	}

	delayStr := form.Value["delay"]
	delay := 10 // default delay
	if len(delayStr) > 0 {
		var err error
		delay, err = strconv.Atoi(delayStr[0])
		if err != nil || delay < 0 {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid delay value"})
		}
	}

	appendReverted := false
	if len(form.Value["appendReverted"]) > 0 {
		appendReverted, _ = strconv.ParseBool(form.Value["appendReverted"][0])
	}

	// Create temporary files for images
	var imagePaths []string
	for _, file := range images {
		tempFile, err := file.Open()
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to open image"})
		}
		defer tempFile.Close()

		data, err := ioutil.ReadAll(tempFile)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to read image"})
		}

		tempFilePath := fmt.Sprintf("/tmp/%s", file.Filename)
		if err := ioutil.WriteFile(tempFilePath, data, 0644); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save image"})
		}
		imagePaths = append(imagePaths, tempFilePath)
	}

	// Prepare ImageMagick command
	targetSizeStr := targetSize[0]
	cmdArgs := []string{"convert"}
	cmdArgs = append(cmdArgs, imagePaths...)
	if appendReverted {
		for i := len(imagePaths) - 1; i >= 0; i-- {
			cmdArgs = append(cmdArgs, imagePaths[i])
		}
	}
	cmdArgs = append(cmdArgs, "-resize", targetSizeStr, "-delay", strconv.Itoa(delay), "-loop", "0", "output.gif")

	// Execute ImageMagick command
	cmd := exec.Command("magick", cmdArgs...)
	if err := cmd.Run(); err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create GIF"})
	}

	// Serve the created GIF
	c.Set("Content-Type", "image/gif")
	c.SendFile("output.gif")

	// Clean up temporary files
	for _, path := range imagePaths {
		os.Remove(path)
	}
	os.Remove("output.gif")

	return nil
}