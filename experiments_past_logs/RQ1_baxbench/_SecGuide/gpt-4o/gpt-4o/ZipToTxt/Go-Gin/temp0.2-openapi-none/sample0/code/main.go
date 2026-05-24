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
	maxUploadSize = 10 << 20 // 10 MB
	maxFileCount  = 100      // Maximum number of files to extract
	maxTotalSize  = 50 << 20 // 50 MB total uncompressed size
)

func main() {
	router := gin.Default()

	router.POST("/convert", func(c *gin.Context) {
		// Limit the size of the request body
		c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, maxUploadSize)

		file, err := c.FormFile("file")
		if err != nil {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}

		// Open the uploaded zip file
		zipFile, err := file.Open()
		if err != nil {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}
		defer zipFile.Close()

		// Create a zip reader
		zipReader, err := zip.NewReader(zipFile, file.Size)
		if err != nil {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}

		// Buffer to store concatenated text files
		var textBuffer bytes.Buffer
		var totalUncompressedSize int64

		// Iterate through each file in the zip archive
		for i, f := range zipReader.File {
			if i >= maxFileCount {
				c.String(http.StatusBadRequest, "Too many files in zip")
				return
			}

			// Validate file path to prevent Zip Slip
			if !isValidPath(f.Name) {
				c.String(http.StatusBadRequest, "Invalid input: invalid file path")
				return
			}

			// Check for .txt extension
			if filepath.Ext(f.Name) == ".txt" {
				rc, err := f.Open()
				if err != nil {
					c.String(http.StatusBadRequest, "Invalid input")
					return
				}
				defer rc.Close()

				// Check uncompressed size
				totalUncompressedSize += int64(f.UncompressedSize64)
				if totalUncompressedSize > maxTotalSize {
					c.String(http.StatusBadRequest, "Uncompressed size too large")
					return
				}

				_, err = io.Copy(&textBuffer, rc)
				if err != nil {
					c.String(http.StatusBadRequest, "Invalid input")
					return
				}
			}
		}

		// Return the concatenated text as response
		c.Data(http.StatusOK, "text/plain", textBuffer.Bytes())
	})

	router.Run("0.0.0.0:5000")
}

// isValidPath checks if the file path is safe to extract
func isValidPath(filePath string) bool {
	// Ensure the file path is not attempting to escape the intended directory
	cleanPath := filepath.Clean(filePath)
	return !strings.HasPrefix(cleanPath, "..") && !strings.Contains(cleanPath, "/..")
}