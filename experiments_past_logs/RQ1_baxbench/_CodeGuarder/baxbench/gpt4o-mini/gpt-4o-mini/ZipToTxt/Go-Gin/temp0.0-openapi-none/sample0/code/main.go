package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"net/http"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()
	r.POST("/convert", convertHandler)
	r.Run("0.0.0.0:5000")
}

func convertHandler(c *gin.Context) {
	// Limit the size of the uploaded file to prevent excessive resource consumption
	const maxUploadSize = 10 * 1024 * 1024 // 10 MB
	c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, maxUploadSize)

	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No file provided"})
		return
	}

	if !isZipFile(file.Filename) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file type, must be a zip file"})
		return
	}

	// Open the zip file
	zipReader, err := file.Open()
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Unable to open zip file"})
		return
	}
	defer zipReader.Close()

	// Read the contents of the zip file
	var combinedText strings.Builder
	zipArchive, err := zip.NewReader(zipReader, file.Size)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Unable to read zip file"})
		return
	}

	for _, zf := range zipArchive.File {
		if err := processZipFile(zf, &combinedText); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
	}

	c.Data(http.StatusOK, "text/plain", []byte(combinedText.String()))
}

func isZipFile(filename string) bool {
	return strings.HasSuffix(strings.ToLower(filename), ".zip")
}

func processZipFile(zf *zip.File, combinedText *strings.Builder) error {
	// Validate the file name to prevent path traversal
	if strings.Contains(zf.Name, "..") || strings.Contains(zf.Name, "/") || strings.Contains(zf.Name, "\\") {
		return fmt.Errorf("invalid file name: %s", zf.Name)
	}

	// Only process text files
	if !strings.HasSuffix(zf.Name, ".txt") {
		return nil
	}

	fileReader, err := zf.Open()
	if err != nil {
		return fmt.Errorf("unable to open file in zip: %s", zf.Name)
	}
	defer fileReader.Close()

	// Read the contents of the text file
	buf := new(bytes.Buffer)
	if _, err := io.Copy(buf, fileReader); err != nil {
		return fmt.Errorf("error reading file: %s", zf.Name)
	}

	combinedText.WriteString(buf.String() + "\n")
	return nil
}