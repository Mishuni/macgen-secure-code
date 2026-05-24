package main

import (
	"fmt"
	"os"
	"os/exec"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Post("/extract", func(c *fiber.Ctx) error {
		videoFileName := c.FormValue("videoFileName")
		frameNumberStr := c.FormValue("frameNumber")
		video, err := c.FormFile("video")
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Failed to upload video."})
		}

		// Save the uploaded video to a temporary file
		tempVideoPath := "./" + videoFileName
		if err := c.SaveFile(video, tempVideoPath); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save video."})
		}
		defer os.Remove(tempVideoPath) // Cleanup temporary video file

		frameNumber, err := strconv.Atoi(frameNumberStr)
		if err != nil || frameNumber < 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid frame number."})
		}

		// Extract the frame using ffmpeg
		outputImagePath := fmt.Sprintf("./frame_%d.png", frameNumber)
		cmd := exec.Command("ffmpeg", "-i", tempVideoPath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImagePath)
		if err := cmd.Run(); err != nil {
			if strings.Contains(err.Error(), "Invalid frame") || strings.Contains(err.Error(), "No such file or directory") {
				return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
			}
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to extract frame."})
		}
		defer os.Remove(outputImagePath) // Cleanup extracted image file

		// Send the extracted image back to the user
		return c.SendFile(outputImagePath, false)
	})

	app.Listen(":5000")
}