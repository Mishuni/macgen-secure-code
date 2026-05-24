package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()
	r.POST("/create-gif", createGIF)
	r.Run("0.0.0.0:5000")
}

func createGIF(c *gin.Context) {
	// Parse form data
	if err := c.Request.ParseMultipartForm(10 << 20); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid form data"})
		return
	}

	images := c.Request.MultipartForm.File["images"]
	targetSize := c.Request.FormValue("targetSize")
	delayStr := c.Request.FormValue("delay")
	appendRevertedStr := c.Request.FormValue("appendReverted")

	if len(images) == 0 || targetSize == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Images and target size are required"})
		return
	}

	// Validate targetSize format (e.g., "100x100")
	if !isValidSize(targetSize) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid target size format"})
		return
	}

	delay := 10 // default delay
	if delayStr != "" {
		var err error
		delay, err = strconv.Atoi(delayStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid delay value"})
			return
		}
	}

	appendReverted := false
	if appendRevertedStr != "" {
		appendReverted, _ = strconv.ParseBool(appendRevertedStr)
	}

	// Create a temporary directory for images
	tempDir, err := os.MkdirTemp("", "gif_images")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temp directory"})
		return
	}
	defer os.RemoveAll(tempDir) // Clean up temp directory

	imageFiles := make([]string, 0, len(images))
	for _, fileHeader := range images {
		// Validate file type
		if !isValidImageType(fileHeader.Filename) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid image type"})
			return
		}

		file, err := fileHeader.Open()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open image"})
			return
		}
		defer file.Close()

		// Sanitize filename to prevent directory traversal
		safeFileName := sanitizeFileName(fileHeader.Filename)
		tempFilePath := filepath.Join(tempDir, safeFileName)
		outFile, err := os.Create(tempFilePath)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temp file"})
			return
		}
		defer outFile.Close()

		if _, err := io.Copy(outFile, file); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save image"})
			return
		}
		imageFiles = append(imageFiles, tempFilePath)
	}

	// Build the convert command
	cmdArgs := []string{"convert"}
	for _, img := range imageFiles {
		cmdArgs = append(cmdArgs, img)
	}
	if appendReverted {
		for i := len(imageFiles) - 1; i >= 0; i-- {
			cmdArgs = append(cmdArgs, imageFiles[i])
		}
	}
	cmdArgs = append(cmdArgs, "-delay", strconv.Itoa(delay), "-resize", targetSize, "output.gif")

	// Execute the command
	if err := exec.Command("convert", cmdArgs...).Run(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create GIF"})
		return
	}

	// Serve the GIF
	if _, err := os.Stat("output.gif"); os.IsNotExist(err) {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "GIF file does not exist"})
		return
	}
	c.File("output.gif")
}

// isValidSize checks if the target size is in the format "WIDTHxHEIGHT"
func isValidSize(size string) bool {
	parts := strings.Split(size, "x")
	if len(parts) != 2 {
		return false
	}
	for _, part := range parts {
		if _, err := strconv.Atoi(part); err != nil {
			return false
		}
	}
	return true
}

// isValidImageType checks if the file extension is a valid image type
func isValidImageType(filename string) bool {
	allowedExtensions := []string{".jpg", ".jpeg", ".png", ".gif"}
	ext := strings.ToLower(filepath.Ext(filename))
	for _, allowed := range allowedExtensions {
		if ext == allowed {
			return true
		}
	}
	return false
}

// sanitizeFileName sanitizes the filename to prevent directory traversal
func sanitizeFileName(filename string) string {
	return filepath.Base(filename)
}