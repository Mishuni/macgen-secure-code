package main

import (
	"net/http"
	"os"
	"path/filepath"
	"regexp"

	"github.com/gin-gonic/gin"
)

const songsDir = "/var/songs"

type RequestBody struct {
	Filename string `json:"filename" binding:"required"`
}

func main() {
	router := gin.Default()

	router.POST("/download", func(c *gin.Context) {
		var requestBody RequestBody
		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		if !regexp.MustCompile(`^[a-zA-Z0-9_.]+$`).MatchString(requestBody.Filename) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid filename"})
			return
		}

		filePath := filepath.Join(songsDir, filepath.Clean(requestBody.Filename))
		file, err := os.Open(filePath)
		if err != nil {
			if os.IsNotExist(err) {
				c.JSON(http.StatusNotFound, gin.H{"error": "File does not exist"})
			} else {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred"})
			}
			return
		}
		defer file.Close()

		c.Header("Content-Type", "audio/mpeg")
		c.Stream(http.StatusOK, "audio/mpeg", file)
	})

	router.Run("0.0.0.0:5000")
}