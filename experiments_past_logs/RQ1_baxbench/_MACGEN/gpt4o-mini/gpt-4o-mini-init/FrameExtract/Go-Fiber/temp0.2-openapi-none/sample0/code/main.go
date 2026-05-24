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

func isValidFileName(fileName string) bool {
	// Check for invalid characters in the filename
	return !strings.ContainsAny(fileName, `<>:"/\|?*`)
}

func main() {
	app := fiber.New()

	app.Post("/extract", func(c *fiber.Ctx) error {
		// Parse the multipart form data
		videoFileName := c.FormValue("videoFileName")
		frameNumberStr := c.FormValue("frameNumber")

		// Validate video file name
		if !isValidFileName(videoFileName) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid video file name."})
		}

		// Validate frame number
		frameNumber, err := strconv.Atoi(frameNumberStr)
		if err != nil || frameNumber < 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid frame number."})
		}

		// Get the uploaded video file
		videoFile, err := c.FormFile("video")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Video file is required."})
		}

		// Save the uploaded video file
		videoPath := filepath.Join(os.TempDir(), videoFile.Filename)
		if err := c.SaveFile(videoFile, videoPath); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save video file."})
		}
		defer os.Remove(videoPath)

		// Prepare the output frame path
		framePath := filepath.Join(os.TempDir(), fmt.Sprintf("frame_%d.png", frameNumber))

		// Extract the frame using ffmpeg
		cmd := exec.Command("ffmpeg", "-i", videoPath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", framePath)
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
		}
		defer os.Remove(framePath)

		// Return the extracted frame
		return c.SendFile(framePath, false)
	})

	app.Listen(":5000")
}