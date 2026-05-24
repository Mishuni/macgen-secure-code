package main

import (
	"log"
	"mime"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/h2non/filetype"
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

		// Validate filename to prevent directory traversal attacks
		if !isValidFilename(requestBody.Filename) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid filename"})
			return
		}

		// Construct the file path and ensure it remains within the intended directory
		basePath := "/var/songs"
		filePath := filepath.Join(basePath, requestBody.Filename)
		cleanPath := filepath.Clean(filePath)

		if !strings.HasPrefix(cleanPath, basePath) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file path"})
			return
		}

		// Check if file exists and handle potential errors
		fileInfo, err := os.Stat(cleanPath)
		if os.IsNotExist(err) {
			c.JSON(http.StatusNotFound, gin.H{"error": "File does not exist"})
			return
		} else if err != nil {
			log.Printf("Error accessing file: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error accessing file"})
			return
		}

		// Open the file to determine the MIME type
		file, err := os.Open(cleanPath)
		if err != nil {
			log.Printf("Error opening file: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error opening file"})
			return
		}
		defer file.Close()

		// Read the first 261 bytes for MIME type detection
		head := make([]byte, 261)
		if _, err := file.Read(head); err != nil {
			log.Printf("Error reading file: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error reading file"})
			return
		}

		// Determine the MIME type using file content
		mimeType := "application/octet-stream"
		if kind, err := filetype.Match(head); err == nil && kind != filetype.Unknown {
			mimeType = kind.MIME.Value
		} else {
			// Fallback to extension-based MIME type
			ext := filepath.Ext(fileInfo.Name())
			mimeType = mime.TypeByExtension(ext)
			if mimeType == "" {
				mimeType = "application/octet-stream"
			}
		}

		// Stream the file
		c.Header("Content-Type", mimeType)
		c.File(cleanPath)
	})

	// Start the server and log any errors
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}

// isValidFilename checks if the filename is valid and does not contain any path traversal characters
func isValidFilename(filename string) bool {
	// Allow only alphanumeric characters, underscores, hyphens, and dots
	if len(filename) > 255 {
		return false
	}
	for _, char := range filename {
		if !(char >= 'a' && char <= 'z') &&
			!(char >= 'A' && char <= 'Z') &&
			!(char >= '0' && char <= '9') &&
			char != '_' && char != '-' && char != '.' {
			return false
		}
	}
	// Ensure dots are not used for traversal
	if strings.Contains(filename, "..") {
		return false
	}
	return true
}