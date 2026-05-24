package main

import (
	"bytes"
	"fmt"
	"github.com/gin-gonic/gin"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
)

func main() {
	router := gin.Default()
	router.POST("/create-gif", createGifHandler)
	router.Run("0.0.0.0:5000")
}

func createGifHandler(c *gin.Context) {
	form, err := c.MultipartForm()
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid form data"})
		return
	}

	files := form.File["images"]
	if len(files) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No images provided"})
		return
	}

	targetSize := c.PostForm("targetSize")
	if !isValidTargetSize(targetSize) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid target size format"})
		return
	}

	delayStr := c.DefaultPostForm("delay", "10")
	delay, err := strconv.Atoi(delayStr)
	if err != nil || delay < 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid delay value"})
		return
	}

	appendReverted := c.DefaultPostForm("appendReverted", "false") == "true"

	tempDir, err := os.MkdirTemp("", "gifcreator")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temp directory"})
		return
	}
	defer os.RemoveAll(tempDir)

	var imagePaths []string
	for _, file := range files {
		filePath := filepath.Join(tempDir, filepath.Clean(file.Filename))
		if err := c.SaveUploadedFile(file, filePath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save uploaded file"})
			return
		}
		imagePaths = append(imagePaths, filePath)
	}

	if appendReverted {
		for i := len(imagePaths) - 1; i >= 0; i-- {
			imagePaths = append(imagePaths, imagePaths[i])
		}
	}

	outputGifPath := filepath.Join(tempDir, "output.gif")
	args := append([]string{"-delay", strconv.Itoa(delay), "-resize", targetSize}, imagePaths...)
	args = append(args, outputGifPath)

	cmd := exec.Command("convert", args...)
	if err := cmd.Run(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create GIF"})
		return
	}

	outputFile, err := os.Open(outputGifPath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open output GIF"})
		return
	}
	defer outputFile.Close()

	var buf bytes.Buffer
	if _, err := io.Copy(&buf, outputFile); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read output GIF"})
		return
	}

	c.Data(http.StatusOK, "image/gif", buf.Bytes())
}

func isValidTargetSize(size string) bool {
	re := regexp.MustCompile(`^\d+x\d+$`)
	return re.MatchString(size)
}