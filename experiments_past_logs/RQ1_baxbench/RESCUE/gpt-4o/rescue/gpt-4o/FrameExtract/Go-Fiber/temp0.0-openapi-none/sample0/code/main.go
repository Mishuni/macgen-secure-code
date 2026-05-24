package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
)

const uploadDir = "./uploads"
const outputDir = "./frames"

func main() {
	// Create necessary directories
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		log.Fatalf("Failed to create upload directory: %v", err)
	}
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		log.Fatalf("Failed to create output directory: %v", err)
	}

	// Initialize Fiber app
	app := fiber.New()

	// Define the /extract endpoint
	app.Post("/extract", func(c *fiber.Ctx) error {
		// Parse multipart form data
		form, err := c.MultipartForm()
		if err != nil {
			return fiber.NewError(fiber.StatusBadRequest, "Invalid form data")
		}

		// Retrieve video file
		videoFileHeader := form.File["video"]
		if len(videoFileHeader) == 0 {
			return fiber.NewError(fiber.StatusBadRequest, "Video file is required")
		}
		videoFile := videoFileHeader[0]

		// Sanitize and validate video file name
		videoFileName := filepath.Base(videoFile.Filename)
		if strings.Contains(videoFileName, "..") || strings.Contains(videoFileName, "/") || strings.Contains(videoFileName, "\\") {
			return fiber.NewError(fiber.StatusBadRequest, "Invalid video file name")
		}

		// Save the uploaded video file
		videoFilePath := filepath.Join(uploadDir, videoFileName)
		if err := c.SaveFile(videoFile, videoFilePath); err != nil {
			return fiber.NewError(fiber.StatusInternalServerError, "Failed to save video file")
		}

		// Retrieve frame number
		frameNumberStr := form.Value["frameNumber"]
		if len(frameNumberStr) == 0 {
			return fiber.NewError(fiber.StatusBadRequest, "Frame number is required")
		}
		frameNumber, err := strconv.Atoi(frameNumberStr[0])
		if err != nil || frameNumber < 0 {
			return fiber.NewError(fiber.StatusBadRequest, "Invalid frame number")
		}

		// Generate output frame file path
		outputFileName := fmt.Sprintf("frame_%d.png", frameNumber)
		outputFilePath := filepath.Join(outputDir, outputFileName)

		// Use ffmpeg to extract the frame
		cmd := exec.Command("ffmpeg", "-i", videoFilePath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputFilePath)
		cmd.Stderr = os.Stderr // Log ffmpeg errors for debugging
		if err := cmd.Run(); err != nil {
			return fiber.NewError(fiber.StatusNotFound, fmt.Sprintf("Frame at index %d could not be found", frameNumber))
		}

		// Serve the extracted frame
		return c.SendFile(outputFilePath, true)
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}