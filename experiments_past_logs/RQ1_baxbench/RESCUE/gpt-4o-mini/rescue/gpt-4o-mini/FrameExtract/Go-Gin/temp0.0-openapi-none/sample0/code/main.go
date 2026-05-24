package main

import (
	"fmt"
	"net/http"
	"os/exec"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

const OUTPUT_DIR = "./output/"

func main() {
	// Create output directory if it doesn't exist
	if err := createOutputDir(); err != nil {
		panic(err)
	}

	r := gin.Default()
	r.POST("/extract", extractFrame)
	r.Run("0.0.0.0:5000")
}

func createOutputDir() error {
	if err := exec.Command("mkdir", "-p", OUTPUT_DIR).Run(); err != nil {
		return fmt.Errorf("failed to create output directory: %w", err)
	}
	return nil
}

func extractFrame(c *gin.Context) {
	videoFileName := c.PostForm("videoFileName")
	frameNumberStr := c.PostForm("frameNumber")
	videoFile, err := c.FormFile("video")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid video file"})
		return
	}

	// Sanitize and validate inputs
	if err := validateInputs(videoFileName, frameNumberStr); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	frameNumber, _ := strconv.Atoi(frameNumberStr)
	outputImagePath := OUTPUT_DIR + "frame_" + strconv.Itoa(frameNumber) + ".png"

	// Extract the frame using ffmpeg
	if err := extractFrameWithFFmpeg(videoFileName, frameNumber, outputImagePath); err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
		return
	}

	c.File(outputImagePath)
}

func validateInputs(videoFileName, frameNumberStr string) error {
	if !strings.HasSuffix(videoFileName, ".mp4") {
		return fmt.Errorf("video file must be an mp4 file")
	}
	if _, err := strconv.Atoi(frameNumberStr); err != nil {
		return fmt.Errorf("frame number must be an integer")
	}
	return nil
}

func extractFrameWithFFmpeg(videoFileName string, frameNumber int, outputImagePath string) error {
	cmd := exec.Command("ffmpeg", "-i", videoFileName, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vsync", "vfr", outputImagePath)
	return cmd.Run()
}