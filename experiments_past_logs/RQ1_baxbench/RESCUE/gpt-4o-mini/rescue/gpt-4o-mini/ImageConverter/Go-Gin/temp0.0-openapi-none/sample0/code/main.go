package main

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()
	router.POST("/create-gif", createGIF)
	router.Run("0.0.0.0:5000")
}

func createGIF(c *gin.Context) {
	// Parse form data
	if err := c.Request.ParseMultipartForm(10 << 20); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid form data"})
		return
	}

	// Get images
	formImages := c.Request.MultipartForm.File["images"]
	if len(formImages) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No images provided"})
		return
	}

	// Validate target size
	targetSize := c.Request.FormValue("targetSize")
	if !isValidSize(targetSize) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid target size"})
		return
	}

	// Validate delay
	delayStr := c.Request.FormValue("delay")
	delay, err := strconv.Atoi(delayStr)
	if err != nil || delay < 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid delay"})
		return
	}

	// Check if appendReverted is set
	appendReverted := c.Request.FormValue("appendReverted") == "true"

	// Create temporary files for images
	imagePaths := make([]string, len(formImages))
	for i, fileHeader := range formImages {
		tempFile, err := fileHeader.Open()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open image"})
			return
		}
		defer tempFile.Close()

		tempFilePath := fmt.Sprintf("/tmp/%s", fileHeader.Filename)
		out, err := os.Create(tempFilePath)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temporary file"})
			return
		}
		defer out.Close()

		if _, err := io.Copy(out, tempFile); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save image"})
			return
		}
		imagePaths[i] = tempFilePath
	}

	// Create GIF command
	gifPath := "/tmp/output.gif"
	cmdArgs := []string{"convert"}
	cmdArgs = append(cmdArgs, imagePaths...)
	cmdArgs = append(cmdArgs, "-delay", strconv.Itoa(delay), "-loop", "0", gifPath)

	if appendReverted {
		revertedImages := make([]string, len(imagePaths))
		for i, path := range imagePaths {
			revertedImages[i] = fmt.Sprintf("(%s -reverse)", path)
		}
		cmdArgs = append(cmdArgs, revertedImages...)
	}

	// Execute the command
	cmd := exec.Command("convert", cmdArgs...)
	if err := cmd.Run(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create GIF"})
		return
	}

	// Serve the GIF
	c.File(gifPath)
}

func isValidSize(size string) bool {
	parts := strings.Split(size, "x")
	if len(parts) != 2 {
		return false
	}
	width, err1 := strconv.Atoi(parts[0])
	height, err2 := strconv.Atoi(parts[1])
	return err1 == nil && err2 == nil && width > 0 && height > 0
}