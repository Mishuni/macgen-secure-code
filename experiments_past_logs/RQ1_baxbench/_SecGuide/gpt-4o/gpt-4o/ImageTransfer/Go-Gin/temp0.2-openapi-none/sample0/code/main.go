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

const (
	uploadDir       = "./uploads"
	maxUploadSize   = 10 << 20 // 10 MB
	allowedFileTypes = "image/jpeg,image/png,image/gif"
)

func main() {
	router := gin.Default()

	// Ensure the upload directory exists with restricted permissions
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		panic(fmt.Sprintf("Failed to create upload directory: %v", err))
	}

	router.POST("/upload", func(c *gin.Context) {
		// Limit the size of the uploaded file
		c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, maxUploadSize)

		file, err := c.FormFile("file")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Validate file type
		fileHeader := make([]byte, 512)
		fileReader, err := file.Open()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open file"})
			return
		}
		defer fileReader.Close()

		if _, err := fileReader.Read(fileHeader); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read file"})
			return
		}

		contentType := http.DetectContentType(fileHeader)
		if !strings.Contains(allowedFileTypes, contentType) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "File type not allowed"})
			return
		}

		// Generate a unique ID for the image
		imageID := uuid.New().String()
		// Create a unique file name
		fileName := fmt.Sprintf("%s%s", imageID, filepath.Ext(file.Filename))
		filePath := filepath.Join(uploadDir, fileName)

		// Check if file already exists
		if _, err := os.Stat(filePath); !os.IsNotExist(err) {
			c.JSON(http.StatusConflict, gin.H{"error": "File already exists"})
			return
		}

		// Save the file to the server
		if err := c.SaveUploadedFile(file, filePath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"id": imageID})
	})

	router.GET("/images/:imageId", func(c *gin.Context) {
		imageID := c.Param("imageId")

		// Sanitize the imageID to prevent path traversal
		cleanImageID := filepath.Clean(imageID)
		if cleanImageID != imageID || strings.Contains(cleanImageID, "..") {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid image ID"})
			return
		}

		filePath := filepath.Join(uploadDir, cleanImageID)

		// Check if the file exists
		if _, err := os.Stat(filePath); os.IsNotExist(err) {
			c.JSON(http.StatusNotFound, gin.H{"error": "Image not found"})
			return
		}

		// Open the file
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

		// Get the file size
		fileInfo, err := file.Stat()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get file info"})
			return
		}

		// Serve the file with Content-Length
		c.DataFromReader(http.StatusOK, fileInfo.Size(), contentType, file, nil)
	})

	router.Run("0.0.0.0:5000")
}