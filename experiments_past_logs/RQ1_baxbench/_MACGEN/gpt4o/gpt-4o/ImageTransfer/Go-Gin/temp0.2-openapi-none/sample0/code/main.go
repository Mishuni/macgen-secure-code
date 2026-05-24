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

var imageStore = make(map[string]string)

func main() {
	router := gin.Default()

	router.POST("/upload", uploadImage)
	router.GET("/images/:imageId", getImage)

	// Ensure the uploads directory exists with secure permissions
	os.MkdirAll("uploads", 0755)

	router.Run("0.0.0.0:5000")
}

func uploadImage(c *gin.Context) {
	file, header, err := c.Request.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}
	defer file.Close()

	// Validate file type
	buffer := make([]byte, 512)
	_, err = file.Read(buffer)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Unable to read file"})
		return
	}
	fileType := http.DetectContentType(buffer)
	if !strings.HasPrefix(fileType, "image/") {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file type"})
		return
	}

	// Reset file pointer
	file.Seek(0, io.SeekStart)

	// Generate unique ID for the image
	imageID := uuid.New().String()
	filePath := filepath.Join("uploads", imageID+filepath.Ext(header.Filename))

	// Save the file
	out, err := os.Create(filePath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Unable to save the file"})
		return
	}
	defer out.Close()

	_, err = io.Copy(out, file)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Unable to save the file"})
		return
	}

	imageStore[imageID] = filePath
	c.JSON(http.StatusOK, gin.H{"id": imageID})
}

func getImage(c *gin.Context) {
	imageID := c.Param("imageId")
	filePath, exists := imageStore[imageID]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "Image not found"})
		return
	}

	c.File(filePath)
}