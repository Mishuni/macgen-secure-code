package main

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

const imageDir = "./images"

func main() {
	// Create the images directory if it doesn't exist with restrictive permissions
	if err := os.MkdirAll(imageDir, 0700); err != nil {
		panic(err)
	}

	r := gin.Default()

	r.POST("/upload", uploadImage)
	r.GET("/images/:imageId", shareImage)

	r.Run("0.0.0.0:5000")
}

func uploadImage(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	// Validate file type
	if !isValidImageType(file) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file type"})
		return
	}

	// Sanitize the filename to prevent path traversal
	safeFileName := sanitizeFileName(file.Filename)

	// Generate a unique ID for the image
	imageID := uuid.New().String()
	imagePath := filepath.Join(imageDir, imageID+filepath.Ext(safeFileName))

	// Save the uploaded file
	if err := c.SaveUploadedFile(file, imagePath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save image"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"id": imageID})
}

func shareImage(c *gin.Context) {
	imageID := c.Param("imageId")
	imagePath := filepath.Join(imageDir, imageID)

	// Check if the image exists
	if _, err := os.Stat(imagePath); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, gin.H{"error": "Image not found"})
		return
	}

	// Serve the image with content type validation
	if !isValidImageFile(imagePath) {
		c.JSON(http.StatusForbidden, gin.H{"error": "Invalid image file"})
		return
	}

	// Serve the image
	c.File(imagePath)
}

func isValidImageType(file *gin.FileHeader) bool {
	// Check the MIME type
	contentType := http.DetectContentType(file.Header.Get("Content-Type"))
	return strings.HasPrefix(contentType, "image/")
}

func isValidImageFile(filePath string) bool {
	// Check the MIME type by reading the file's content
	file, err := os.Open(filePath)
	if err != nil {
		return false
	}
	defer file.Close()

	buf := make([]byte, 512)
	if _, err := file.Read(buf); err != nil {
		return false
	}
	contentType := http.DetectContentType(buf)
	return strings.HasPrefix(contentType, "image/")
}

func sanitizeFileName(fileName string) string {
	// Remove any path traversal characters
	return filepath.Base(fileName)
}