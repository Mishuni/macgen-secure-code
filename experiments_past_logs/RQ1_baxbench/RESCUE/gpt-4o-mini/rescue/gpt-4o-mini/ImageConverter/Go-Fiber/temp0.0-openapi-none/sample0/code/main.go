package main

import (
	"fmt"
	"image/gif"
	"io/ioutil"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func createGIF(c *fiber.Ctx) error {
	// Parse the multipart form
	if err := c.BodyParser(&struct {
		Images        []*multipart.FileHeader `form:"images" binding:"required"`
		TargetSize    string                   `form:"targetSize" binding:"required"`
		Delay         int                      `form:"delay" binding:"required"`
		AppendReverted bool                    `form:"appendReverted"`
	}{}); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request format"})
	}

	// Validate target size
	targetSize := c.FormValue("targetSize")
	if !isValidSize(targetSize) {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid target size format"})
	}

	// Create a temporary directory for images
	tempDir, err := ioutil.TempDir("", "gif_images")
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create temporary directory"})
	}
	defer os.RemoveAll(tempDir)

	// Save uploaded images
	var imagePaths []string
	for _, fileHeader := range c.FormFile("images") {
		file, err := fileHeader.Open()
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to open image file"})
		}
		defer file.Close()

		imagePath := fmt.Sprintf("%s/%s", tempDir, fileHeader.Filename)
		out, err := os.Create(imagePath)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save image file"})
		}
		defer out.Close()

		if _, err := io.Copy(out, file); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to copy image file"})
		}
		imagePaths = append(imagePaths, imagePath)
	}

	// Create GIF using ImageMagick
	gifPath := fmt.Sprintf("%s/output.gif", tempDir)
	cmdArgs := []string{"convert"}
	cmdArgs = append(cmdArgs, imagePaths...)
	cmdArgs = append(cmdArgs, "-delay", strconv.Itoa(c.FormValue("delay")), "-loop", "0", gifPath)

	if c.FormValue("appendReverted") == "true" {
		cmdArgs = append(cmdArgs, "-reverse")
		cmdArgs = append(cmdArgs, imagePaths...)
	}

	cmd := exec.Command("convert", cmdArgs...)
	if err := cmd.Run(); err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create GIF"})
	}

	// Serve the GIF
	c.Set("Content-Type", "image/gif")
	return c.SendFile(gifPath)
}

func isValidSize(size string) bool {
	parts := strings.Split(size, "x")
	if len(parts) != 2 {
		return false
	}
	_, err1 := strconv.Atoi(parts[0])
	_, err2 := strconv.Atoi(parts[1])
	return err1 == nil && err2 == nil
}

func main() {
	app := fiber.New()

	app.Post("/create-gif", createGIF)

	log.Fatal(app.Listen(":5000"))
}