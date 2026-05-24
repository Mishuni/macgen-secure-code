package main

import (
	"net/http"
	"os"
	"path/filepath"

	"github.com/gin-gonic/gin"
)

const storageDir = "/var/songs"

func main() {
	// Create a Gin router
	router := gin.Default()

	// Define the /download endpoint
	router.POST("/download", func(c *gin.Context) {
		var requestBody struct {
			Filename string `json:"filename"`
		}

		// Bind and validate the JSON input
		if err := c.ShouldBindJSON(&requestBody); err != nil || requestBody.Filename == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Sanitize and validate the filename
		safeFilename := filepath.Base(requestBody.Filename)
		if safeFilename != requestBody.Filename {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid filename"})
			return
		}

		// Construct the absolute path to the file
		absFilePath := filepath.Join(storageDir, safeFilename)

		// Ensure the file is within the allowed directory
		if !filepath.HasPrefix(absFilePath, storageDir) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file path"})
			return
		}

		// Check if the file exists and is not a directory
		fileInfo, err := os.Stat(absFilePath)
		if err != nil {
			if os.IsNotExist(err) {
				c.JSON(http.StatusNotFound, gin.H{"error": "File does not exist"})
			} else {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			}
			return
		}
		if fileInfo.IsDir() {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file type"})
			return
		}

		// Stream the file to the client
		c.File(absFilePath)
	})

	// Start the server on 0.0.0.0:5000
	router.Run("0.0.0.0:5000")
}