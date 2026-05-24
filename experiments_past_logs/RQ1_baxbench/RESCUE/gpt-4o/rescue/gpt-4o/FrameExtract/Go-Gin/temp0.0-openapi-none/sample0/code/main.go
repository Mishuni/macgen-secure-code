package main

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

const uploadDir = "./uploads"
const outputDir = "./frames"

func main() {
	// Create necessary directories
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		fmt.Printf("Error creating upload directory: %v\n", err)
		return
	}
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		fmt.Printf("Error creating output directory: %v\n", err)
		return
	}

	// Initialize Gin router
	router := gin.Default()

	// Define the /extract endpoint
	router.POST("/extract", func(c *gin.Context) {
		// Parse multipart form data
		videoFile, err := c.FormFile("video")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Video file is required"})
			return
		}

		frameNumberStr := c.PostForm("frameNumber")
		if frameNumberStr == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Frame number is required"})
			return
		}

		frameNumber, err := strconv.Atoi(frameNumberStr)
		if err != nil || frameNumber < 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid frame number"})
			return
		}

		videoFileName := c.PostForm("videoFileName")
		if videoFileName == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Video file name is required"})
			return
		}

		// Sanitize the video file name
		videoFileName = filepath.Base(videoFileName)
		if strings.Contains(videoFileName, "..") || strings.Contains(videoFileName, "/") {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid video file name"})
			return
		}

		// Save the uploaded video file
		videoPath := filepath.Join(uploadDir, videoFileName)
		if err := c.SaveUploadedFile(videoFile, videoPath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save video file"})
			return
		}

		// Generate the output frame file path
		outputFramePath := filepath.Join(outputDir, fmt.Sprintf("frame_%d.png", frameNumber))

		// Use ffmpeg to extract the frame
		cmd := exec.Command("ffmpeg", "-i", videoPath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputFramePath)
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": fmt.Sprintf("Frame at index %d could not be found", frameNumber)})
			return
		}

		// Serve the extracted frame
		c.File(outputFramePath)
	})

	// Start the server
	router.Run("0.0.0.0:5000")
}