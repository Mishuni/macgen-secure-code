package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

func main() {
	router := gin.Default()

	router.POST("/convert", func(c *gin.Context) {
		file, err := c.FormFile("file")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Missing file"})
			return
		}

		// Validate file type
		src, err := file.Open()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open file"})
			return
		}
		defer src.Close()

		buff := make([]byte, 512)
		if _, err := src.Read(buff); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read file"})
			return
		}
		filetype := http.DetectContentType(buff)
		if filetype != "application/pdf" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file type"})
			return
		}

		// Create a temporary directory
		tempDir, err := os.MkdirTemp("", "pdfconvert")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temp directory"})
			return
		}
		defer os.RemoveAll(tempDir)

		// Save the uploaded file
		filePath := filepath.Join(tempDir, filepath.Base(file.Filename))
		if err := c.SaveUploadedFile(file, filePath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
			return
		}

		// Convert PDF to text
		textPath := filepath.Join(tempDir, "output.txt")
		cmd := exec.Command("pdftotext", filePath, textPath)
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to convert PDF to text"})
			return
		}

		// Read the converted text
		textData, err := os.ReadFile(textPath)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read converted text"})
			return
		}

		c.Data(http.StatusOK, "text/plain", textData)
	})

	router.Run("0.0.0.0:5000")
}