package main

import (
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
)

func main() {
	app := fiber.New()

	app.Post("/extract", func(c *fiber.Ctx) error {
		// Parse the multipart form:
		form, err := c.MultipartForm()
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid form data"})
		}

		// Get the video file:
		videoFileHeader := form.File["video"]
		if len(videoFileHeader) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Video file is required"})
		}

		videoFile, err := videoFileHeader[0].Open()
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Could not open video file"})
		}
		defer videoFile.Close()

		// Generate a unique temporary file path for the video:
		videoFilePath := filepath.Join(os.TempDir(), uuid.New().String()+".mp4")
		outFile, err := os.Create(videoFilePath)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Could not save video file"})
		}
		defer outFile.Close()

		_, err = io.Copy(outFile, videoFile)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Could not read video file"})
		}

		// Get the frame number:
		frameNumberStr := form.Value["frameNumber"]
		if len(frameNumberStr) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Frame number is required"})
		}

		frameNumber, err := strconv.Atoi(frameNumberStr[0])
		if err != nil || frameNumber < 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid frame number"})
		}

		// Generate a unique temporary file path for the frame:
		frameFilePath := filepath.Join(os.TempDir(), uuid.New().String()+".png")

		// Extract the frame using ffmpeg:
		cmd := exec.Command("ffmpeg", "-i", videoFilePath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", frameFilePath)
		err = cmd.Run()
		if err != nil {
			os.Remove(videoFilePath)
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
		}

		// Send the extracted frame:
		err = c.SendFile(frameFilePath, true)
		if err != nil {
			os.Remove(videoFilePath)
			os.Remove(frameFilePath)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Could not send extracted frame"})
		}

		// Clean up temporary files:
		os.Remove(videoFilePath)
		os.Remove(frameFilePath)

		return nil
	})

	app.Listen("0.0.0.0:5000")
}