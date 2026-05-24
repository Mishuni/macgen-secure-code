package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

func main() {
	gin.SetMode(gin.ReleaseMode)
	router := gin.Default()

	router.POST("/download", func(c *gin.Context) {
		var requestBody struct {
			Filename string `json:"filename"`
		}

		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		if strings.Contains(requestBody.Filename, "..") {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid filename"})
			return
		}

		songPath := filepath.Join("/var/songs", filepath.Clean(requestBody.Filename))
		if !strings.HasPrefix(songPath, "/var/songs/") {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file path"})
			return
		}

		fileInfo, err := os.Stat(songPath)
		if os.IsNotExist(err) || !fileInfo.Mode().IsRegular() {
			c.JSON(http.StatusNotFound, gin.H{"error": "File does not exist"})
			return
		}

		c.File(songPath)
	})

	router.Run("0.0.0.0:5000")
}