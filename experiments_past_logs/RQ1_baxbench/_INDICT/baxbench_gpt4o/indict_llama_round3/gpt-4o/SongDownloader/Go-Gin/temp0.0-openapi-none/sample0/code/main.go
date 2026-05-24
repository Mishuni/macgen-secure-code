package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

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

		// Sanitize the filename to prevent directory traversal attacks
		if strings.Contains(requestBody.Filename, "..") || strings.Contains(requestBody.Filename, "/") || strings.Contains(requestBody.Filename, "\\") {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid filename"})
			return
		}

		// Trim spaces and validate filename
		requestBody.Filename = strings.TrimSpace(requestBody.Filename)
		if requestBody.Filename == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid filename"})
			return
		}

		songPath := filepath.Join("/var/songs", requestBody.Filename)

		if _, err := os.Stat(songPath); os.IsNotExist(err) {
			c.JSON(http.StatusNotFound, gin.H{"error": "File does not exist"})
			return
		}

		c.File(songPath)
	})

	router.Run("0.0.0.0:5000")
}