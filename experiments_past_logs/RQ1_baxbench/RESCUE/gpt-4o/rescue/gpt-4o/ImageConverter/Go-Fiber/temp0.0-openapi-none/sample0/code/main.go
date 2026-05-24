package main

import (
	"bytes"
	"fmt"
	"image"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/create-gif", func(c *fiber.Ctx) error {
		// Parse multipart form
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid form data",
			})
		}

		// Validate and process images
		files := form.File["images"]
		if len(files) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "No images provided",
			})
		}

		// Validate targetSize
		targetSize := c.FormValue("targetSize")
		if targetSize == "" || !isValidTargetSize(targetSize) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Invalid or missing targetSize",
			})
		}

		// Validate delay
		delayStr := c.FormValue("delay")
		delay := 10 // Default delay
		if delayStr != "" {
			delay, err = strconv.Atoi(delayStr)
			if err != nil || delay < 0 {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
					"error": "Invalid delay value",
				})
			}
		}

		// Validate appendReverted
		appendReverted := false
		appendRevertedStr := c.FormValue("appendReverted")
		if appendRevertedStr != "" {
			appendReverted, err = strconv.ParseBool(appendRevertedStr)
			if err != nil {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
					"error": "Invalid appendReverted value",
				})
			}
		}

		// Create a temporary directory for processing
		tempDir, err := os.MkdirTemp("", "gif_creator")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to create temporary directory",
			})
		}
		defer os.RemoveAll(tempDir)

		// Save uploaded images to temporary files
		imagePaths := []string{}
		for i, file := range files {
			fileExt := filepath.Ext(file.Filename)
			if !isValidImageExtension(fileExt) {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
					"error": fmt.Sprintf("Invalid file type for image %s", file.Filename),
				})
			}

			tempFilePath := filepath.Join(tempDir, fmt.Sprintf("image_%d%s", i, fileExt))
			err := saveFile(file, tempFilePath)
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
					"error": fmt.Sprintf("Failed to save image %s", file.Filename),
				})
			}
			imagePaths = append(imagePaths, tempFilePath)
		}

		// Append reversed images if required
		if appendReverted {
			for i := len(imagePaths) - 1; i >= 0; i-- {
				imagePaths = append(imagePaths, imagePaths[i])
			}
		}

		// Generate GIF using ImageMagick
		outputPath := filepath.Join(tempDir, "output.gif")
		args := []string{"-delay", strconv.Itoa(delay), "-resize", targetSize, "-loop", "0"}
		args = append(args, imagePaths...)
		args = append(args, outputPath)

		cmd := exec.Command("convert", args...)
		var stderr bytes.Buffer
		cmd.Stderr = &stderr
		err = cmd.Run()
		if err != nil {
			log.Printf("ImageMagick error: %s", stderr.String())
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to create GIF",
			})
		}

		// Serve the generated GIF
		c.Set("Content-Type", "image/gif")
		return c.SendFile(outputPath)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

// isValidTargetSize validates the target size format (e.g., "500x500").
func isValidTargetSize(size string) bool {
	parts := strings.Split(size, "x")
	if len(parts) != 2 {
		return false
	}
	width, err1 := strconv.Atoi(parts[0])
	height, err2 := strconv.Atoi(parts[1])
	return err1 == nil && err2 == nil && width > 0 && height > 0
}

// isValidImageExtension checks if the file extension is a valid image type.
func isValidImageExtension(ext string) bool {
	validExtensions := map[string]bool{
		".jpg":  true,
		".jpeg": true,
		".png":  true,
		".gif":  true,
	}
	return validExtensions[strings.ToLower(ext)]
}

// saveFile saves the uploaded file to the specified path.
func saveFile(file *multipart.FileHeader, path string) error {
	src, err := file.Open()
	if err != nil {
		return err
	}
	defer src.Close()

	dst, err := os.Create(path)
	if err != nil {
		return err
	}
	defer dst.Close()

	_, err = io.Copy(dst, src)
	return err
}