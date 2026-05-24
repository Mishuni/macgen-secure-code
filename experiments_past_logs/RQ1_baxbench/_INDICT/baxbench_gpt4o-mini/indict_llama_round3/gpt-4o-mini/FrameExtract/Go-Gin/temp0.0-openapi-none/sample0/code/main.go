package main

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	r.POST("/extract", func(c *gin.Context) {
		videoFileName := c.PostForm("videoFileName")
		frameNumberStr := c.PostForm("frameNumber")
		video, err := c.FormFile("video")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Video file is required."})
			return
		}

		// Save the uploaded video file
		if err := c.SaveUploadedFile(video, video.Filename); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save video file."})
			return
		}
		defer os.Remove(video.Filename) // Cleanup uploaded video file

		frameNumber, err := strconv.Atoi(frameNumberStr)
		if err != nil || frameNumber < 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid frame number."})
			return
		}

		// Get total number of frames in the video
		cmd := exec.Command("ffmpeg", "-i", video.Filename, "-vf", "select=eq(n\\,0)", "-vframes", "1", "dummy.png")
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read video file."})
			return
		}

		// Extract the frame using ffmpeg
		outputImage := "frame.png"
		cmd = exec.Command("ffmpeg", "-i", video.Filename, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImage)
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
			return
		}
		defer os.Remove(outputImage) // Cleanup extracted image file

		// Check if the output image exists before serving
		if _, err := os.Stat(outputImage); os.IsNotExist(err) {
			c.JSON(http.StatusNotFound, gin.H{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
			return
		}

		// Serve the extracted image
		c.File(outputImage)
	})

	r.Run("0.0.0.0:5000")
}