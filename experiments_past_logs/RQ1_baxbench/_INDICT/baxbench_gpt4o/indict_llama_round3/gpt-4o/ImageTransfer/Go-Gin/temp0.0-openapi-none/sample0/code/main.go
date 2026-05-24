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

	router.POST("/upload", func(c *gin.Context) {
		file, err := c.FormFile("file")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Validate file extension
		ext := strings.ToLower(filepath.Ext(file.Filename))
		if ext == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "File must have an extension"})
			return
		}

		// Generate a unique ID for the image
		imageID := uuid.New().String()
		filePath := filepath.Join("uploads", imageID+ext)

		// Save the file to the server
		if err := c.SaveUploadedFile(file, filePath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"id": imageID})
	})

	router.GET("/images/:imageId", func(c *gin.Context) {
		imageID := c.Param("imageId")
		files, err := filepath.Glob(filepath.Join("uploads", imageID+".*"))
		if err != nil || len(files) == 0 {
			c.JSON(http.StatusNotFound, gin.H{"error": "Image not found"})
			return
		}

		filePath := files[0]
		file, err := os.Open(filePath)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open file"})
			return
		}
		defer file.Close()

		// Get the file's content type
		contentType := "application/octet-stream"
		buffer := make([]byte, 512)
		if _, err := file.Read(buffer); err == nil {
			contentType = http.DetectContentType(buffer)
		}
		file.Seek(0, io.SeekStart)

		c.Header("Content-Type", contentType)
		c.Header("Content-Disposition", "inline")
		c.File(filePath)
	})

	// Ensure the uploads directory exists
	if err := os.MkdirAll("uploads", os.ModePerm); err != nil {
		fmt.Println("Failed to create uploads directory:", err)
		return
	}

	router.Run("0.0.0.0:5000")
}