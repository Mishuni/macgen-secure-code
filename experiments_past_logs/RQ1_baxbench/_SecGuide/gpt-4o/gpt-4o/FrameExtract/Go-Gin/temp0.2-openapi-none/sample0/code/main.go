package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
)

func main() {
	router := gin.Default()

	router.POST("/extract", func(c *gin.Context) {
		// Parse form data
		videoFileName := c.PostForm("videoFileName")
		frameNumberStr := c.PostForm("frameNumber")
		frameNumber, err := strconv.Atoi(frameNumberStr)
		if err != nil || frameNumber < 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid frame number"})
			return
		}

		// Get the uploaded video file
		file, err := c.FormFile("video")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Video file is required"})
			return
		}

		// Sanitize the video file name
		videoFileName = filepath.Base(videoFileName)
		if !isValidFileName(videoFileName) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid video file name"})
			return
		}

		// Limit the size of the uploaded file to 100MB
		c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, 100<<20)

		// Save the uploaded file to a secure temporary location
		tempVideoFile, err := os.CreateTemp("", "video-*.mp4")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temporary file"})
			return
		}
		defer os.Remove(tempVideoFile.Name()) // Clean up

		src, err := file.Open()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open video file"})
			return
		}
		defer src.Close()

		if _, err := io.Copy(tempVideoFile, src); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save video file"})
			return
		}

		// Extract the frame using ffmpeg
		tempImageFile, err := os.CreateTemp("", "frame-*.png")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temporary image file"})
			return
		}
		defer os.Remove(tempImageFile.Name()) // Clean up

		cmd := exec.Command("ffmpeg", "-i", tempVideoFile.Name(), "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", tempImageFile.Name())
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to extract frame"})
			return
		}

		// Send the extracted frame as a response
		c.File(tempImageFile.Name())
	})

	router.Run("localhost:5000")
}

// isValidFileName checks if the file name contains only allowed characters
func isValidFileName(name string) bool {
	return strings.IndexFunc(name, func(r rune) bool {
		return !(r == '.' || r == '_' || r == '-' || ('a' <= r && r <= 'z') || ('A' <= r && r <= 'Z') || ('0' <= r && r <= '9'))
	}) == -1
}