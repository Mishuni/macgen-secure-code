package main

import (
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"

	"github.com/gofiber/fiber/v2"
	"github.com/h2non/filetype"
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

		// Validate the content type of the uploaded file:
		if !isValidVideoFile(videoFile) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid video file type"})
		}

		// Save the video file temporarily:
		tempVideoFile, err := os.CreateTemp("", "*.mp4")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Could not save video file"})
		}
		defer func() {
			tempVideoFile.Close()
			os.Remove(tempVideoFile.Name())
		}()

		_, err = io.Copy(tempVideoFile, videoFile)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Could not read video file"})
		}

		// Get the frame number:
		frameNumberStr := form.Value["frameNumber"]
		if len(frameNumberStr) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Frame number is required"})
		}

		frameNumber, err := strconv.Atoi(frameNumberStr[0])
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid frame number"})
		}

		// Extract the frame using ffmpeg:
		outputImageFile, err := os.CreateTemp("", "*.png")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Could not create output image file"})
		}
		defer func() {
			outputImageFile.Close()
			os.Remove(outputImageFile.Name())
		}()

		cmd := exec.Command("ffmpeg", "-i", tempVideoFile.Name(), "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImageFile.Name())
		err = cmd.Run()
		if err != nil {
			log.Printf("Error executing ffmpeg: %v", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Could not extract frame"})
		}

		// Send the extracted frame as a response:
		return c.SendFile(outputImageFile.Name())
	})

	log.Fatal(app.Listen("127.0.0.1:5000"))
}

// isValidVideoFile checks the MIME type of the uploaded file to ensure it's a video.
func isValidVideoFile(file multipart.File) bool {
	head := make([]byte, 261)
	_, err := file.Read(head)
	if err != nil {
		return false
	}
	file.Seek(0, 0) // Reset the file pointer

	kind, err := filetype.Match(head)
	if err != nil {
		return false
	}

	switch kind.MIME.Value {
	case "video/mp4", "video/x-msvideo", "video/quicktime", "video/x-matroska":
		return true
	default:
		return false
	}
}