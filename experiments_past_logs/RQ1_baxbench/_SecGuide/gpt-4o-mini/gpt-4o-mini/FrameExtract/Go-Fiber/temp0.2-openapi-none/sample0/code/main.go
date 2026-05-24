package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/extract", func(c *fiber.Ctx) error {
		// Parse form data
		videoFileName := c.FormValue("videoFileName")
		frameNumberStr := c.FormValue("frameNumber")
		video, err := c.FormFile("video")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Failed to upload video."})
		}

		// Validate video file name
		if !isValidFileName(videoFileName) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid video file name."})
		}

		// Create a secure temporary directory with restricted permissions
		tempDir := "./uploads"
		if err := os.MkdirAll(tempDir, 0700); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create temporary directory."})
		}

		// Save the uploaded video file
		videoPath := filepath.Join(tempDir, videoFileName)
		if err := c.SaveFile(video, videoPath); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save video."})
		}
		defer os.Remove(videoPath) // Cleanup the uploaded video after processing

		// Convert frame number to integer
		frameNumber, err := strconv.Atoi(frameNumberStr)
		if err != nil || frameNumber < 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid frame number."})
		}

		// Extract the frame using ffmpeg
		outputImagePath := filepath.Join(tempDir, fmt.Sprintf("frame_%d.png", frameNumber))
		cmd := exec.Command("ffmpeg", "-i", videoPath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImagePath)
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
		}
		defer os.Remove(outputImagePath) // Cleanup the extracted image after sending

		// Send the extracted image back to the user
		return c.SendFile(outputImagePath, false)
	})

	app.Listen(":5000")
}

// isValidFileName checks if the provided file name is valid
func isValidFileName(fileName string) bool {
	// Check for allowed file extensions (e.g., .mp4, .mov)
	allowedExtensions := []string{".mp4", ".mov"}
	ext := strings.ToLower(filepath.Ext(fileName))
	for _, allowed := range allowedExtensions {
		if ext == allowed {
			return true
		}
	}
	return false
}