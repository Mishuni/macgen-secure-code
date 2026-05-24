package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

const (
	uploadDir = "./uploads"
)

func main() {
	// Create the uploads directory if it doesn't exist
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
			c.String(http.StatusBadRequest, "Invalid file upload")
			return
		}

		// Validate the file extension
		if !strings.HasSuffix(file.Filename, ".zip") {
			c.String(http.StatusBadRequest, "Only .zip files are allowed")
			return
		}

		// Save the uploaded file to a temporary location
		tempFilePath := filepath.Join(uploadDir, filepath.Base(file.Filename))
		if err := c.SaveUploadedFile(file, tempFilePath); err != nil {
			c.String(http.StatusInternalServerError, "Failed to save uploaded file")
			return
		}
		defer os.Remove(tempFilePath) // Ensure the temporary file is deleted after processing

		// Process the zip file
		output, err := processZipFile(tempFilePath)
		if err != nil {
			c.String(http.StatusInternalServerError, "Failed to process zip file: %v", err)
			return
		}

		// Return the concatenated text as the response
		c.Data(http.StatusOK, "text/plain", output)
	})

	// Start the server on 0.0.0.0:5000
	router.Run("0.0.0.0:5000")
}

// processZipFile extracts and concatenates the contents of all text files in the zip file
func processZipFile(zipPath string) ([]byte, error) {
	// Open the zip file
	zipReader, err := zip.OpenReader(zipPath)
	if err != nil {
		return nil, fmt.Errorf("failed to open zip file: %w", err)
	}
	defer zipReader.Close()

	var buffer bytes.Buffer

	// Iterate through the files in the zip archive
	for _, file := range zipReader.File {
		// Skip directories
		if file.FileInfo().IsDir() {
			continue
		}

		// Validate the file extension
		if !strings.HasSuffix(file.Name, ".txt") {
			continue
		}

		// Open the file inside the zip archive
		fileReader, err := file.Open()
		if err != nil {
			return nil, fmt.Errorf("failed to open file in zip: %w", err)
		}

		// Read the file contents
		_, err = io.Copy(&buffer, fileReader)
		fileReader.Close() // Ensure the file is closed after reading
		if err != nil {
			return nil, fmt.Errorf("failed to read file in zip: %w", err)
		}

		// Add a newline to separate contents of different files
		buffer.WriteString("\n")
	}

	return buffer.Bytes(), nil
}