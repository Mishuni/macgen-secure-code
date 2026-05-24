package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
)

const maxUploadSize = 10 << 20 // 10 MB
const maxExtractedSize = 50 << 20 // 50 MB

func main() {
	router := gin.Default()

	router.POST("/convert", func(c *gin.Context) {
		c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, maxUploadSize)
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

		// Create a buffer to store the zip file content
		var zipBuffer bytes.Buffer
		_, err = io.Copy(&zipBuffer, zipFile)
		if err != nil {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}

		zipReader, err := zip.NewReader(bytes.NewReader(zipBuffer.Bytes()), file.Size)
		if err != nil {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}

		var buffer bytes.Buffer
		var totalExtractedSize int64

		for _, f := range zipReader.File {
			if !f.FileInfo().IsDir() && strings.HasSuffix(f.Name, ".txt") {
				fileInZip, err := f.Open()
				if err != nil {
					c.String(http.StatusBadRequest, "Invalid input")
					return
				}
				defer fileInZip.Close()

				fileSize := f.FileInfo().Size()
				if totalExtractedSize+fileSize > maxExtractedSize {
					c.String(http.StatusBadRequest, "Extracted content too large")
					return
				}

				_, err = io.Copy(&buffer, fileInZip)
				if err != nil {
					c.String(http.StatusBadRequest, "Invalid input")
					return
				}
				buffer.WriteString("\n") // Add a newline between files
				totalExtractedSize += fileSize
			}
		}

		c.Data(http.StatusOK, "text/plain", buffer.Bytes())
	})

	router.Run("0.0.0.0:5000")
}