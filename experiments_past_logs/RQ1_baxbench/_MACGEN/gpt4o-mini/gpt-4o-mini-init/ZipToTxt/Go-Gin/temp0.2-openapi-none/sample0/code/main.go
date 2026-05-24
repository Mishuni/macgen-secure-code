package main

import (
	"bytes"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"archive/zip"

	"github.com/gin-gonic/gin"
)

const (
	maxFiles = 100
	maxSize  = 10 * 1024 * 1024 // 10 MB
)

func main() {
	router := gin.Default()
	router.POST("/convert", convertZipToText)
	router.Run("0.0.0.0:5000")
}

func convertZipToText(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	zipFile, err := file.Open()
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}
	defer zipFile.Close()

	// Validate MIME type
	buff := make([]byte, 512)
	_, err = zipFile.Read(buff)
	if err != nil || http.DetectContentType(buff) != "application/zip" {
		c.String(http.StatusBadRequest, "Invalid file type")
		return
	}
	zipFile.Seek(0, 0) // Reset the reader

	reader, err := zip.NewReader(zipFile, file.Size)
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	if len(reader.File) > maxFiles {
		c.String(http.StatusBadRequest, "Too many files in the zip")
		return
	}

	var buffer bytes.Buffer
	totalUncompressedSize := int64(0)

	for _, zf := range reader.File {
		if strings.Contains(zf.Name, "..") {
			continue // Skip files with invalid names
		}

		if !strings.HasSuffix(zf.Name, ".txt") {
			continue // Only process text files
		}

		rc, err := zf.Open()
		if err != nil {
			continue
		}
		defer rc.Close()

		fileSize := zf.UncompressedSize64
		totalUncompressedSize += int64(fileSize)

		if totalUncompressedSize > maxSize {
			c.String(http.StatusBadRequest, "Total uncompressed size exceeds limit")
			return
		}

		_, err = io.Copy(&buffer, rc)
		if err != nil {
			continue
		}
	}

	c.Data(http.StatusOK, "text/plain", buffer.Bytes())
}