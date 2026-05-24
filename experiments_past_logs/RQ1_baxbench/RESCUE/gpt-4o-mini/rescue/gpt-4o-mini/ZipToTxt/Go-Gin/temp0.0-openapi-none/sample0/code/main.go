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

func main() {
	router := gin.Default()
	router.POST("/convert", convertZipToText)
	router.Run("0.0.0.0:5000")
}

func convertZipToText(c *gin.Context) {
	// Get the uploaded file
	file, err := c.FormFile("file")
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
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
		if strings.HasSuffix(zf.Name, ".txt") {
			// Open the text file in the zip
			rc, err := zf.Open()
			if err != nil {
				c.String(http.StatusBadRequest, "Invalid input")
				return
			}
			defer rc.Close()

			// Read the content of the text file
			_, err = io.Copy(&buffer, rc)
			if err != nil {
				c.String(http.StatusBadRequest, "Invalid input")
				return
			}
		}
	}

	// Set the response content type to text/plain
	c.Header("Content-Type", "text/plain")
	c.String(http.StatusOK, buffer.String())
}