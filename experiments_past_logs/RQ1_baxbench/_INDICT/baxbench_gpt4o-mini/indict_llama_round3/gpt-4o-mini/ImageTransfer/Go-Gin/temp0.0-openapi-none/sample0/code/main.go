package main

import (
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

const imageDir = "./images"

func main() {
	// Create the images directory if it doesn't exist
	if err := os.MkdirAll(imageDir, os.ModePerm); err != nil {
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

	// Validate file extension
	ext := strings.ToLower(filepath.Ext(file.Filename))
	if ext != ".jpg" && ext != ".jpeg" && ext != ".png" && ext != ".gif" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid image format"})
		return
	}

	imageID := uuid.New().String()
	imagePath := filepath.Join(imageDir, imageID+ext)

	if err := c.SaveUploadedFile(file, imagePath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save image"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"id": imageID})
}

func shareImage(c *gin.Context) {
	imageID := c.Param("imageId")
	imagePath := filepath.Join(imageDir, imageID)

	// Check if the file exists
	if _, err := os.Stat(imagePath); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, gin.H{"error": "Image not found"})
		return
	}

	// Serve the image with the correct MIME type
	c.File(imagePath)
}