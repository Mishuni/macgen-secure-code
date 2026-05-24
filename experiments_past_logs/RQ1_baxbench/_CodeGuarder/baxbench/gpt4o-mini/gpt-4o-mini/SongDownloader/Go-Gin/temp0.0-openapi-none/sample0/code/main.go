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
	router.POST("/download", downloadSong)
	router.Run("0.0.0.0:5000")
}

func downloadSong(c *gin.Context) {
	var requestBody struct {
		Filename string `json:"filename" binding:"required"`
	}

	if err := c.ShouldBindJSON(&requestBody); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	filename := filepath.Base(requestBody.Filename)
	filePath := filepath.Join(songsDir, filename)

	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, gin.H{"error": "File does not exist"})
		return
	}

	c.Header("Content-Type", "audio/mpeg")
	c.Header("Content-Disposition", "attachment; filename="+filename)
	c.File(filePath)
}