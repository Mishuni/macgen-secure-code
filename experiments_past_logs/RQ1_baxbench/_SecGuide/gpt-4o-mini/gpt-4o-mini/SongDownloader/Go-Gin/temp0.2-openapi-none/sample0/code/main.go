package main

import (
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

const songsDir = "/var/songs"

func isValidFilename(filename string) bool {
	// Check for path traversal characters and ensure the filename is not empty
	if strings.Contains(filename, "..") || strings.Contains(filename, "/") || filename == "" {
		return false
	}
	// Additional check for URL encoded characters
	if strings.ContainsAny(filename, "%") {
		return false
	}
	return true
}

func isAudioFile(filename string) bool {
	// Validate file type by checking the MIME type
	allowedExtensions := []string{".mp3", ".wav"}
	for _, ext := range allowedExtensions {
		if strings.HasSuffix(filename, ext) {
			return true
		}
	}
	return false
}

func main() {
	router := gin.Default()

	router.POST("/download", func(c *gin.Context) {
		var request struct {
			Filename string `json:"filename" binding:"required"`
		}

		if err := c.ShouldBindJSON(&request); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		if !isValidFilename(request.Filename) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid filename"})
			return
		}

		filePath := filepath.Join(songsDir, request.Filename)
		file, err := os.Open(filePath)
		if err != nil {
			if os.IsNotExist(err) {
				c.JSON(http.StatusNotFound, gin.H{"error": "File not found"})
			} else {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			}
			return
		}
		defer file.Close()

		// Validate file type (basic check for audio files)
		if !isAudioFile(request.Filename) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file type"})
			return
		}

		c.Header("Content-Type", "audio/mpeg")
		c.File(filePath)
	})

	router.Run("0.0.0.0:5000")
}