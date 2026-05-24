package main

import (
	"net/http"
	"os"
	"path/filepath"

	"github.com/gin-gonic/gin"
)

const songsDir = "/var/songs"

func main() {
	router := gin.Default()

	router.POST("/download", func(c *gin.Context) {
		var requestBody struct {
			Filename string `json:"filename" binding:"required"`
		}

		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Sanitize and validate the filename
		if !isValidFilename(requestBody.Filename) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid filename"})
			return
		}

		// Construct the absolute path
		absPath := filepath.Join(songsDir, requestBody.Filename)

		// Check if the file exists
		if _, err := os.Stat(absPath); os.IsNotExist(err) {
			c.JSON(http.StatusNotFound, gin.H{"error": "File does not exist"})
			return
		}

		// Stream the file
		c.File(absPath)
	})

	router.Run("0.0.0.0:5000")
}

// isValidFilename checks if the filename is valid and does not contain any path traversal characters
func isValidFilename(filename string) bool {
	// Check for invalid characters (e.g., path traversal)
	if filepath.Base(filename) != filename {
		return false
	}
	return true
}