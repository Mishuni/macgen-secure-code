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

	// Open the uploaded zip file
	src, err := file.Open()
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}
	defer src.Close()

	// Read the zip file
	zipReader, err := zip.NewReader(src, file.Size)
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	var buffer bytes.Buffer
	hasTextFiles := false

	// Iterate through the files in the zip archive
	for _, zf := range zipReader.File {
		if strings.HasSuffix(zf.Name, ".txt") {
			hasTextFiles = true
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

	if !hasTextFiles {
		c.String(http.StatusBadRequest, "No text files found in the zip")
		return
	}

	// Return the concatenated text
	c.Data(http.StatusOK, "text/plain", buffer.Bytes())
}