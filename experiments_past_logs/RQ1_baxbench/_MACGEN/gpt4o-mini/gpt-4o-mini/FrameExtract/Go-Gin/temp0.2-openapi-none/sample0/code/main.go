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

const maxUploadSize = 10 * 1024 * 1024 // 10 MB

func main() {
	r := gin.Default()
	r.POST("/extract", extractFrame)
	r.Run("0.0.0.0:5000")
}

func extractFrame(c *gin.Context) {
	// Limit the size of the uploaded file
	c.Request.ParseMultipartForm(maxUploadSize)

	videoFile, err := c.FormFile("video")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Video file is required."})
		return
	}

	// Validate frame number
	frameNumberStr := c.PostForm("frameNumber")
	frameNumber, err := strconv.Atoi(frameNumberStr)
	if err != nil || frameNumber < 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Frame number must be a positive integer."})
		return
	}

	// Validate file type
	file, err := videoFile.Open()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open video file."})
		return
	}
	defer file.Close()

	buffer := make([]byte, 512)
	if _, err := file.Read(buffer); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read video file."})
		return
	}
	contentType := http.DetectContentType(buffer)
	if contentType != "video/mp4" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Only MP4 video files are allowed."})
		return
	}

	// Save the uploaded video file to a secure location
	videoPath := filepath.Join("/tmp/uploads", videoFile.Filename)
	if err := c.SaveUploadedFile(videoFile, videoPath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save video file."})
		return
	}
	defer os.Remove(videoPath)

	// Prepare output image path
	outputImagePath := filepath.Join("/tmp/uploads", fmt.Sprintf("frame_%d.png", frameNumber))
	cmd := exec.Command("ffmpeg", "-i", videoPath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImagePath)
	if err := cmd.Run(); err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
		return
	}
	defer os.Remove(outputImagePath)

	// Return the extracted image
	c.File(outputImagePath)
}