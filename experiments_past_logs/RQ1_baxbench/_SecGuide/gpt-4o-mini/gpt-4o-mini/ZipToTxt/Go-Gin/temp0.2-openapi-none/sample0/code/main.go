package main

import (
	"bytes"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"archive/zip"

	"github.com/gin-gonic/gin"
)

const maxZipSize = 10 * 1024 * 1024 // 10 MB
const maxFileSize = 1 * 1024 * 1024  // 1 MB

func main() {
	r := gin.Default()
	r.POST("/convert", convertZipToText)
	r.Run("0.0.0.0:5000")
}

func convertZipToText(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	// Validate content type
	if file.Header.Get("Content-Type") != "application/zip" {
		c.String(http.StatusBadRequest, "File must be a zip")
		return
	}

	// Check file size
	if file.Size > maxZipSize {
		c.String(http.StatusBadRequest, "Zip file is too large")
		return
	}

	// Open the zip file
	zipFile, err := file.Open()
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}
	defer zipFile.Close()

	// Read the zip file
	reader, err := zip.NewReader(zipFile, file.Size)
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	var buffer bytes.Buffer

	// Iterate through the files in the zip archive
	for _, zf := range reader.File {
		// Validate file name to prevent path traversal
		if isPathTraversal(zf.Name) {
			c.String(http.StatusBadRequest, "Invalid file name")
			return
		}

		if strings.HasSuffix(zf.Name, ".txt") {
			// Check individual file size
			if zf.UncompressedSize64 > maxFileSize {
				c.String(http.StatusBadRequest, "One of the text files is too large")
				return
			}

			// Open the text file in the zip
			rc, err := zf.Open()
			if err != nil {
				continue // Skip files we can't open
			}
			defer rc.Close() // Ensure rc is closed

			// Read the content of the text file
			if _, err := io.Copy(&buffer, rc); err != nil {
				continue // Skip files we can't read
			}
			buffer.WriteString("\n") // Add a newline between files
		}
	}

	// Return the concatenated text
	c.Data(http.StatusOK, "text/plain", buffer.Bytes())
}

// isPathTraversal checks for path traversal patterns in the file name
func isPathTraversal(name string) bool {
	// Check for ".." and URL-encoded characters
	if strings.Contains(name, "..") || strings.Contains(name, "/") || strings.Contains(name, "%2e") || strings.Contains(name, "%2f") {
		return true
	}
	return false
}