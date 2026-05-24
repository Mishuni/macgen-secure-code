package main

import (
	"fmt"
	"os"
	"os/exec"
	"strconv"

	"github.com/gofiber/fiber/v2"
)

type ExtractRequest struct {
	VideoFileName string `form:"videoFileName" json:"videoFileName"`
	FrameNumber   int    `form:"frameNumber" json:"frameNumber"`
	Video         []byte `form:"video" json:"video"`
}

func extractFrame(c *fiber.Ctx) error {
	var req ExtractRequest

	// Parse the multipart form data
	if err := c.BodyParser(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
	}

	// Validate frame number
	if req.FrameNumber < 0 {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Frame number must be non-negative"})
	}

	// Save the uploaded video file temporarily
	videoPath := fmt.Sprintf("/tmp/%s", req.VideoFileName)
	if err := os.WriteFile(videoPath, req.Video, 0644); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save video file"})
	}
	defer os.Remove(videoPath) // Clean up the temporary file

	// Construct the ffmpeg command to extract the frame
	outputImagePath := fmt.Sprintf("/tmp/frame_%d.png", req.FrameNumber)
	cmd := exec.Command("ffmpeg", "-i", videoPath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", req.FrameNumber), "-vframes", "1", outputImagePath)

	// Execute the command
	if err := cmd.Run(); err != nil {
		return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": fmt.Sprintf("Frame at index %d could not be found.", req.FrameNumber)})
	}

	// Read the extracted image
	imageData, err := os.ReadFile(outputImagePath)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to read extracted image"})
	}

	// Return the extracted image as a binary response
	return c.Status(fiber.StatusOK).Send(imageData)
}

func main() {
	app := fiber.New()

	app.Post("/extract", extractFrame)

	app.Listen(":5000")
}