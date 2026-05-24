package main

import (
	"bytes"
	"fmt"
	"image"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

const storageDir = "./uploads"

func sanitizePath(input string) (string, error) {
	absPath, err := filepath.Abs(input)
	if err != nil {
		return "", err
	}
	if !strings.HasPrefix(absPath, storageDir) {
		return "", fmt.Errorf("invalid path")
	}
	return absPath, nil
}

func validateTargetSize(size string) (string, error) {
	parts := strings.Split(size, "x")
	if len(parts) != 2 {
		return "", fmt.Errorf("invalid target size format")
	}
	width, err := strconv.Atoi(parts[0])
	if err != nil || width <= 0 {
		return "", fmt.Errorf("invalid width in target size")
	}
	height, err := strconv.Atoi(parts[1])
	if err != nil || height <= 0 {
		return "", fmt.Errorf("invalid height in target size")
	}
	return fmt.Sprintf("%dx%d", width, height), nil
}

func validateDelay(delay int) int {
	if delay < 1 {
		return 10 // Default delay
	}
	return delay
}

func main() {
	// Ensure storage directory exists
	if err := os.MkdirAll(storageDir, 0755); err != nil {
		fmt.Printf("Failed to create storage directory: %v\n", err)
		return
	}

	router := gin.Default()

	router.POST("/create-gif", func(c *gin.Context) {
		form, err := c.MultipartForm()
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid form data"})
			return
		}

		// Validate and process images
		files := form.File["images"]
		if len(files) == 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "No images provided"})
			return
		}

		var imagePaths []string
		for _, file := range files {
			filePath := filepath.Join(storageDir, filepath.Base(file.Filename))
			safePath, err := sanitizePath(filePath)
			if err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file path"})
				return
			}
			if err := c.SaveUploadedFile(file, safePath); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
				return
			}
			imagePaths = append(imagePaths, safePath)
		}

		// Validate target size
		targetSize := c.PostForm("targetSize")
		validSize, err := validateTargetSize(targetSize)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid target size"})
			return
		}

		// Validate delay
		delayStr := c.PostForm("delay")
		delay := 10 // Default delay
		if delayStr != "" {
			delay, err = strconv.Atoi(delayStr)
			if err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid delay value"})
				return
			}
		}
		delay = validateDelay(delay)

		// Validate appendReverted
		appendReverted := c.PostForm("appendReverted") == "true"

		// Prepare command arguments
		var args []string
		for _, img := range imagePaths {
			args = append(args, img)
		}
		if appendReverted {
			for i := len(imagePaths) - 1; i >= 0; i-- {
				args = append(args, imagePaths[i])
			}
		}
		args = append(args, "-resize", validSize, "-delay", strconv.Itoa(delay), "-loop", "0", "gif:-")

		// Execute ImageMagick command
		cmd := exec.Command("convert", args...)
		var out bytes.Buffer
		cmd.Stdout = &out
		cmd.Stderr = &out
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create GIF", "details": out.String()})
			return
		}

		// Return the generated GIF
		c.Data(http.StatusOK, "image/gif", out.Bytes())
	})

	router.Run("0.0.0.0:5000")
}