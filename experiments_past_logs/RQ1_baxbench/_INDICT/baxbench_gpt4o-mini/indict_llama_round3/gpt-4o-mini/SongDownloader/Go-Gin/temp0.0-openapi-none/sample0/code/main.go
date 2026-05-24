package main

import (
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

const songsDir = "/var/songs"

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

		// Sanitize the filename to prevent directory traversal attacks
		if strings.ContainsAny(request.Filename, "../") || strings.Contains(request.Filename, "\\") {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid filename"})
			return
		}

		filePath := filepath.Join(songsDir, request.Filename)
		file, err := os.Open(filePath)
		if err != nil {
			if os.IsNotExist(err) {
				c.JSON(http.StatusNotFound, gin.H{"error": "File does not exist"})
			} else {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			}
			return
		}
		defer file.Close()

		c.Header("Content-Type", "audio/mpeg")
		c.Stream(http.StatusOK, "audio/mpeg", file)
	})

	router.Run("0.0.0.0:5000")
}