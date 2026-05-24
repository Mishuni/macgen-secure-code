package main

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	router.POST("/download", func(c *gin.Context) {
		var requestBody struct {
			Filename string `json:"filename" binding:"required"`
		}

		// Parse and validate the request
		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Validate filename to prevent path traversal
		filename := filepath.Base(requestBody.Filename)
		if filename == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid filename"})
			return
		}

		// Construct the full file path
		songPath := filepath.Join("/var/songs", filename)

		// Check if the file exists
		fileInfo, err := os.Stat(songPath)
		if os.IsNotExist(err) || fileInfo.IsDir() {
			c.JSON(http.StatusNotFound, gin.H{"error": "File does not exist"})
			return
		}

		// Stream the song file
		c.Header("Content-Type", "audio/mpeg")
		c.File(songPath)
	})

	// Start the server
	if err := router.Run("0.0.0.0:5000"); err != nil {
		fmt.Printf("Failed to start server: %v\n", err)
	}
}