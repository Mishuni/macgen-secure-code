package main

import (
	"bytes"
	"fmt"
	"github.com/gofiber/fiber/v2"
	"os"
	"os/exec"
	"strconv"
)

func main() {
	app := fiber.New()

	app.Post("/extract", func(c *fiber.Ctx) error {
		// Parse and validate incoming request
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid form data"})
		}

		videoFileHeader := form.File["video"]
		if len(videoFileHeader) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Video file is required"})
		}

		frameNumberStr := form.Value["frameNumber"]
		if len(frameNumberStr) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Frame number is required"})
		}

		frameNumber, err := strconv.Atoi(frameNumberStr[0])
		if err != nil || frameNumber < 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid frame number"})
		}

		// Handle video file upload
		videoFile, err := videoFileHeader[0].Open()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to open video file"})
		}
		defer videoFile.Close()

		tempVideoFile, err := os.CreateTemp("", "uploaded-*.mp4")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create temp file"})
		}
		defer os.Remove(tempVideoFile.Name())

		_, err = tempVideoFile.ReadFrom(videoFile)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save video file"})
		}

		// Extract the specified frame using FFmpeg
		outputImageFile := fmt.Sprintf("frame-%d.png", frameNumber)
		cmd := exec.Command("ffmpeg", "-i", tempVideoFile.Name(), "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImageFile)
		var stderr bytes.Buffer
		cmd.Stderr = &stderr

		if err := cmd.Run(); err != nil {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": fmt.Sprintf("Frame at index %d could not be found. %s", frameNumber, stderr.String())})
		}
		defer os.Remove(outputImageFile)

		// Return the extracted frame
		return c.SendFile(outputImageFile)
	})

	app.Listen("0.0.0.0:5000")
}