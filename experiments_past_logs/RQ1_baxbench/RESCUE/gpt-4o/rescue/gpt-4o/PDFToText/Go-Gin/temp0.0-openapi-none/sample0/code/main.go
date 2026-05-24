package main

import (
	"bytes"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/gin-gonic/gin"
)

const (
	uploadDir = "./uploads"
)

func main() {
	// Create the upload directory if it doesn't exist
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		fmt.Printf("Failed to create upload directory: %v\n", err)
		return
	}

	// Initialize the Gin router
	router := gin.Default()

	// Define the /convert endpoint
	router.POST("/convert", func(c *gin.Context) {
		// Parse the uploaded file
		file, err := c.FormFile("file")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Missing or invalid file"})
			return
		}

		// Sanitize the file name
		filename := filepath.Base(file.Filename)
		if filename == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file name"})
			return
		}

		// Save the uploaded file to a temporary location
		tempFilePath := filepath.Join(uploadDir, filename)
		if err := c.SaveUploadedFile(file, tempFilePath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
			return
		}
		defer os.Remove(tempFilePath) // Ensure the file is removed after processing

		// Validate that the file is a PDF
		if filepath.Ext(tempFilePath) != ".pdf" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Uploaded file is not a PDF"})
			return
		}

		// Extract text from the PDF using the `pdftotext` utility
		text, err := extractTextFromPDF(tempFilePath)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to extract text from PDF"})
			return
		}

		// Return the extracted text as plain text
		c.Data(http.StatusOK, "text/plain; charset=utf-8", []byte(text))
	})

	// Start the server on 0.0.0.0:5000
	router.Run("0.0.0.0:5000")
}

// extractTextFromPDF extracts text from a PDF file using the `pdftotext` utility
func extractTextFromPDF(pdfPath string) (string, error) {
	// Use a temporary file to store the extracted text
	tempTextFile := pdfPath + ".txt"
	defer os.Remove(tempTextFile) // Ensure the temporary text file is removed

	// Execute the `pdftotext` command
	cmd := exec.Command("pdftotext", pdfPath, tempTextFile)
	var stderr bytes.Buffer
	cmd.Stderr = &stderr
	if err := cmd.Run(); err != nil {
		return "", fmt.Errorf("pdftotext error: %v, details: %s", err, stderr.String())
	}

	// Read the extracted text from the temporary file
	text, err := os.ReadFile(tempTextFile)
	if err != nil {
		return "", fmt.Errorf("failed to read extracted text: %v", err)
	}

	return string(text), nil
}