package main

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()
	r.POST("/extract", extractFrame)
	r.Run("0.0.0.0:5000")
}

func extractFrame(c *gin.Context) {
	videoFileName := c.PostForm("videoFileName")
	frameNumber := c.PostForm("frameNumber")
	video, err := c.FormFile("video")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to get video file."})
		return
	}

	// Validate video file name and frame number
	if err := validateInput(videoFileName, frameNumber); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Save the uploaded video file
	videoPath := filepath.Join(os.TempDir(), sanitizeFileName(videoFileName))
	if err := c.SaveUploadedFile(video, videoPath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save video file."})
		return
	}
	defer os.Remove(videoPath) // Clean up the uploaded file

	// Extract the frame using ffmpeg
	frameImagePath := filepath.Join(os.TempDir(), fmt.Sprintf("frame_%s.png", frameNumber))
	cmd := exec.Command("ffmpeg", "-i", videoPath, "-vf", fmt.Sprintf("select=eq(n\\,%s)", frameNumber), "-vframes", "1", frameImagePath)
	if err := cmd.Run(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to extract frame."})
		return
	}
	defer os.Remove(frameImagePath) // Clean up the extracted frame

	// Serve the extracted frame
	c.File(frameImagePath)
}

func validateInput(videoFileName, frameNumber string) error {
	if filepath.Ext(videoFileName) != ".mp4" {
		return fmt.Errorf("invalid video file type, only .mp4 is allowed")
	}

	// Validate frame number to be numeric
	if matched, _ := regexp.MatchString("^[0-9]+$", frameNumber); !matched {
		return fmt.Errorf("frame number must be a positive integer")
	}

	return nil
}

func sanitizeFileName(fileName string) string {
	// Remove any path traversal characters and restrict to safe characters
	re := regexp.MustCompile(`[^a-zA-Z0-9_.-]`)
	return re.ReplaceAllString(fileName, "_")
}