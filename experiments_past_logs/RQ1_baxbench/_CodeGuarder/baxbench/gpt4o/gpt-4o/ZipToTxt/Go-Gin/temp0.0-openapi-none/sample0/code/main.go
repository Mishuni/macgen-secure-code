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

func main() {
	router := gin.Default()
	router.POST("/convert", convertZipToText)
	router.Run("0.0.0.0:5000")
}

func convertZipToText(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid input: %v", err)
		return
	}

	// Open the uploaded zip file
	uploadedFile, err := file.Open()
	if err != nil {
		c.String(http.StatusBadRequest, "Failed to open uploaded file: %v", err)
		return
	}
	defer uploadedFile.Close()

	// Read the zip file into a buffer
	buf := new(bytes.Buffer)
	if _, err := io.Copy(buf, uploadedFile); err != nil {
		c.String(http.StatusBadRequest, "Failed to read uploaded file: %v", err)
		return
	}

	// Open the zip archive
	zipReader, err := zip.NewReader(bytes.NewReader(buf.Bytes()), file.Size)
	if err != nil {
		c.String(http.StatusBadRequest, "Failed to read zip archive: %v", err)
		return
	}

	var concatenatedText strings.Builder

	// Iterate through each file in the zip archive
	for _, zipFile := range zipReader.File {
		if !isValidZipFile(zipFile) {
			c.String(http.StatusBadRequest, "Invalid file in zip archive: %s", zipFile.Name)
			return
		}

		// Open the file inside the zip archive
		fileReader, err := zipFile.Open()
		if err != nil {
			c.String(http.StatusBadRequest, "Failed to open file in zip archive: %v", err)
			return
		}
		defer fileReader.Close()

		// Check if the file is a text file
		if filepath.Ext(zipFile.Name) == ".txt" {
			// Read the file content
			content, err := io.ReadAll(fileReader)
			if err != nil {
				c.String(http.StatusBadRequest, "Failed to read file content: %v", err)
				return
			}
			// Concatenate the content
			concatenatedText.Write(content)
			concatenatedText.WriteString("\n")
		}
	}

	// Return the concatenated text as the response
	c.String(http.StatusOK, concatenatedText.String())
}

func isValidZipFile(zipFile *zip.File) bool {
	// Validate the file path to prevent Zip Slip vulnerability
	destPath := filepath.Join("/tmp", zipFile.Name)
	if !strings.HasPrefix(filepath.Clean(destPath), "/tmp") {
		return false
	}
	return true
}