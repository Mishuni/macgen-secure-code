package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"io"
	"net/http"
	"os"
	"path/filepath"
)

const (
	StorageDir = "./uploads"
)

func main() {
	// Ensure the storage directory exists
	if err := os.MkdirAll(StorageDir, 0755); err != nil {
		fmt.Printf("Failed to create storage directory: %v\n", err)
		return
	}

	r := gin.Default()

	// Route for uploading images
	r.POST("/upload", func(c *gin.Context) {
		file, err := c.FormFile("file")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file input"})
			return
		}

		// Sanitize and validate the file name
		filename := filepath.Base(file.Filename)
		if filename == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file name"})
			return
		}

		// Generate a unique ID for the file
		imageID := uuid.New().String()
		filePath := filepath.Join(StorageDir, imageID+"_"+filename)

		// Save the file securely
		if err := c.SaveUploadedFile(file, filePath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
			return
		}

		// Return the shareable link
		c.JSON(http.StatusOK, gin.H{"id": imageID})
	})

	// Route for viewing images
	r.GET("/images/:imageId", func(c *gin.Context) {
		imageID := c.Param("imageId")

		// Validate the image ID
		if imageID == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid image ID"})
			return
		}

		// Search for the file in the storage directory
		var foundFile string
		err := filepath.Walk(StorageDir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if !info.IsDir() && filepath.Base(path)[:len(imageID)] == imageID {
				foundFile = path
				return io.EOF // Stop walking once the file is found
			}
			return nil
		})
		if err != nil && err != io.EOF {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to search for file"})
			return
		}

		// If no file is found, return 404
		if foundFile == "" {
			c.JSON(http.StatusNotFound, gin.H{"error": "Image not found"})
			return
		}

		// Serve the file with the correct content type
		c.File(foundFile)
	})

	// Start the server
	if err := r.Run("0.0.0.0:5000"); err != nil {
		fmt.Printf("Failed to start server: %v\n", err)
	}
}