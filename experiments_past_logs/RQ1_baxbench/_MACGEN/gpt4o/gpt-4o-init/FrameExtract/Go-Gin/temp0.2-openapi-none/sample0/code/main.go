package main

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

func main() {
	router := gin.New()
	router.Use(gin.Recovery())

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

		tempVideoPath := filepath.Join(os.TempDir(), uuid.New().String()+filepath.Ext(videoFile.Filename))
		if err := c.SaveUploadedFile(videoFile, tempVideoPath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save video file"})
			return
		}
		defer os.Remove(tempVideoPath)

		outputImagePath := filepath.Join(os.TempDir(), uuid.New().String()+".png")
		defer os.Remove(outputImagePath)

		cmd := exec.Command("ffmpeg", "-i", tempVideoPath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImagePath)
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
			return
		}

		c.File(outputImagePath)
	})

	router.Run("0.0.0.0:5000")
}