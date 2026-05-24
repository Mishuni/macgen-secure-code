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
)

func main() {
	router := gin.Default()

	router.POST("/extract", func(c *gin.Context) {
		// Parse and validate request data
		frameNumberStr := c.PostForm("frameNumber")
		frameNumber, err := strconv.Atoi(frameNumberStr)
		if err != nil || frameNumber < 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid frame number"})
			return
		}

		file, err := c.FormFile("video")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Video file is required"})
			return
		}

		// Handle video file upload
		tempDir, err := os.MkdirTemp("", "video-upload-*")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temporary directory"})
			return
		}
		defer os.RemoveAll(tempDir)

		videoPath := filepath.Join(tempDir, file.Filename)
		if err := c.SaveUploadedFile(file, videoPath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save video file"})
			return
		}

		// Extract frame using ffmpeg
		framePath := filepath.Join(tempDir, "frame.png")
		cmd := exec.Command("ffmpeg", "-i", videoPath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", framePath)
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
			return
		}

		// Return extracted frame
		c.File(framePath)
	})

	router.Run("0.0.0.0:5000")
}