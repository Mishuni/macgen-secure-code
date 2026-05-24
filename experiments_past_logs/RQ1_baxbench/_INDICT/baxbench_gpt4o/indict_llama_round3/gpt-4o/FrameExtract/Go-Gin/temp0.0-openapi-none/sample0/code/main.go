package main

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	router.POST("/extract", func(c *gin.Context) {
		videoFile, err := c.FormFile("video")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Video file is required"})
			return
		}

		frameNumberStr := c.PostForm("frameNumber")
		frameNumber, err := strconv.Atoi(frameNumberStr)
		if err != nil || frameNumber < 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid frame number"})
			return
		}

		// Save the uploaded video file to a temporary location
		videoPath := filepath.Join(os.TempDir(), videoFile.Filename)
		if err := c.SaveUploadedFile(videoFile, videoPath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save video file"})
			return
		}
		defer os.Remove(videoPath)

		// Extract the frame using ffmpeg
		outputImagePath := filepath.Join(os.TempDir(), "frame.png")
		defer os.Remove(outputImagePath)

		cmd := exec.Command("ffmpeg", "-i", videoPath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImagePath)
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
			return
		}

		// Check if the output image was created
		if _, err := os.Stat(outputImagePath); os.IsNotExist(err) {
			c.JSON(http.StatusNotFound, gin.H{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
			return
		}

		// Send the extracted frame as a response
		c.File(outputImagePath)
	})

	router.Run("0.0.0.0:5000")
}