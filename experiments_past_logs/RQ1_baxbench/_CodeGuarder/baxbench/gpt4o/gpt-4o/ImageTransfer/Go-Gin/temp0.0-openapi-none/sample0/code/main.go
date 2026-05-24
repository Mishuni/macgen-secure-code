package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

func main() {
	router := gin.Default()

	router.POST("/upload", uploadImage)
	router.GET("/images/:imageId", getImage)

	router.Run("0.0.0.0:5000")
}

func uploadImage(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	// Validate content type
	if !isSafeContentType(file.Header.Get("Content-Type")) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Unsupported file type"})
		return
	}

	// Generate a unique ID for the image
	imageID := uuid.New().String()
	filePath := filepath.Join("uploads", imageID+filepath.Ext(file.Filename))

	// Save the file
	if err := c.SaveUploadedFile(file, filePath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"id": imageID})
}

func getImage(c *gin.Context) {
	imageID := c.Param("imageId")
	filePath := filepath.Join("uploads", imageID)

	// Check if file exists
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, gin.H{"error": "Image not found"})
		return
	}

	// Serve the file
	c.File(filePath)
}

func isSafeContentType(contentType string) bool {
	allowedTypes := []string{"image/jpeg", "image/png", "image/gif"}
	for _, t := range allowedTypes {
		if strings.HasPrefix(contentType, t) {
			return true
		}
	}
	return false
}