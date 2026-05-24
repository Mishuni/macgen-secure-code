package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/gin-gonic/gin"
	"github.com/h2non/filetype"
)

func main() {
	router := gin.Default()

	router.POST("/convert", func(c *gin.Context) {
		file, err := c.FormFile("file")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Missing file"})
			return
		}

		// Validate file extension
		if filepath.Ext(file.Filename) != ".pdf" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file type"})
			return
		}

		// Save the uploaded file to a temporary location
		tempFile, err := os.CreateTemp("", "upload-*.pdf")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temporary file"})
			return
		}
		defer os.Remove(tempFile.Name())

		if err := c.SaveUploadedFile(file, tempFile.Name()); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save uploaded file"})
			return
		}

		// Validate file content type
		buf, err := os.ReadFile(tempFile.Name())
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read uploaded file"})
			return
		}
		if !filetype.IsPDF(buf) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Uploaded file is not a valid PDF"})
			return
		}

		// Use pdftotext to convert PDF to text
		outputFile := tempFile.Name() + ".txt"
		cmd := exec.Command("pdftotext", tempFile.Name(), outputFile)
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to convert PDF to text"})
			return
		}
		defer os.Remove(outputFile)

		// Read the converted text file
		text, err := os.ReadFile(outputFile)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read converted text"})
			return
		}

		c.Data(http.StatusOK, "text/plain", text)
	})

	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Printf("Failed to start server: %v", err)
	}
}