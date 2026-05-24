package main

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

const storageDir = "./uploads/"

func main() {
	// Create the uploads directory if it doesn't exist
	if err := os.MkdirAll(storageDir, os.ModePerm); err != nil {
		fmt.Println("Error creating uploads directory:", err)
		return
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

	// Sanitize the file name
	safeFileName := sanitizeFileName(file.Filename)
	newFilePath := filepath.Join(storageDir, safeFileName)

	// Save the file
	if err := c.SaveUploadedFile(file, newFilePath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}

	// Return the image ID (file name)
	c.JSON(http.StatusOK, gin.H{"id": safeFileName})
}

func shareImage(c *gin.Context) {
	imageId := c.Param("imageId")
	imagePath := filepath.Join(storageDir, imageId)

	// Check if the file exists
	if _, err := os.Stat(imagePath); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, gin.H{"error": "Image not found"})
		return
	}

	// Serve the image
	c.File(imagePath)
}

func sanitizeFileName(fileName string) string {
	// Generate a unique ID for the file to prevent conflicts and ensure safety
	uniqueID := uuid.New().String()
	ext := filepath.Ext(fileName)
	return fmt.Sprintf("%s%s", uniqueID, ext)
}