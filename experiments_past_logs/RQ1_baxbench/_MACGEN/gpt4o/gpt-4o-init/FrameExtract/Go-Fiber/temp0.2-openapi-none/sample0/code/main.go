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
		videoFile, err := c.FormFile("video")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Video file is required"})
		}

		frameNumberStr := c.FormValue("frameNumber")
		frameNumber, err := strconv.Atoi(frameNumberStr)
		if err != nil || frameNumber < 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid frame number"})
		}

		// Validate file extension
		if !strings.HasSuffix(videoFile.Filename, ".mp4") {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Only MP4 videos are allowed"})
		}

		// Save the uploaded video to a temporary file
		videoPath := filepath.Join(os.TempDir(), videoFile.Filename)
		if err := c.SaveFile(videoFile, videoPath); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save video file"})
		}
		defer os.Remove(videoPath)

		// Define the output image path
		outputImagePath := filepath.Join(os.TempDir(), fmt.Sprintf("frame_%d.png", frameNumber))
		defer os.Remove(outputImagePath)

		// Use ffmpeg to extract the frame
		cmd := exec.Command("ffmpeg", "-i", videoPath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImagePath)
		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
		}

		// Check if the output image was created
		if _, err := os.Stat(outputImagePath); os.IsNotExist(err) {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
		}

		// Send the extracted frame as a response
		return c.SendFile(outputImagePath, true)
	})

	app.Listen("0.0.0.0:5000")
}