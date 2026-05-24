package main

import (
	"bytes"
	"fmt"
	"github.com/gin-gonic/gin"
	"io"
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
			c.JSON(http.StatusBadRequest, gin.H{"error": "File is required"})
			return
		}

		// Validate file extension
		if filepath.Ext(file.Filename) != ".pdf" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Only PDF files are allowed"})
			return
		}

		// Open the uploaded file
		src, err := file.Open()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open file"})
			return
		}
		defer src.Close()

		// Create a temporary file to save the uploaded PDF
		tempFile, err := os.CreateTemp("", "upload-*.pdf")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temporary file"})
			return
		}
		defer os.Remove(tempFile.Name())

		// Copy the uploaded file to the temporary file
		if _, err := io.Copy(tempFile, src); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
			return
		}

		// Close the temporary file
		if err := tempFile.Close(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to close temporary file"})
			return
		}

		// Extract text from PDF using pdftotext
		output, err := extractTextFromPDF(tempFile.Name())
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to extract text from PDF"})
			return
		}

		// Return the extracted text
		c.String(http.StatusOK, output)
	})

	router.Run("0.0.0.0:5000")
}

func extractTextFromPDF(pdfPath string) (string, error) {
	cmd := exec.Command("pdftotext", pdfPath, "-")
	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &out

	if err := cmd.Run(); err != nil {
		return "", fmt.Errorf("pdftotext error: %v", err)
	}

	return out.String(), nil
}