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

	if !strings.HasSuffix(file.Filename, ".zip") {
		c.String(http.StatusBadRequest, "Invalid file extension")
		return
	}

	zipFile, err := file.Open()
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}
	defer zipFile.Close()

	buff := make([]byte, 512)
	_, err = zipFile.Read(buff)
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	if http.DetectContentType(buff) != "application/zip" {
		c.String(http.StatusBadRequest, "Invalid file type")
		return
	}

	zipFile.Seek(0, io.SeekStart)
	buf := new(bytes.Buffer)
	_, err = io.Copy(buf, zipFile)
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	reader, err := zip.NewReader(bytes.NewReader(buf.Bytes()), file.Size)
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	const maxFiles = 100
	const maxTotalSize = 10 * 1024 * 1024 // 10 MB
	var totalSize int64
	var result strings.Builder

	for _, f := range reader.File {
		if strings.Contains(f.Name, "..") {
			c.String(http.StatusBadRequest, "Invalid file path")
			return
		}

		totalSize += int64(f.UncompressedSize64)
		if totalSize > maxTotalSize || len(reader.File) > maxFiles {
			c.String(http.StatusBadRequest, "Resource limits exceeded")
			return
		}

		if filepath.Ext(f.Name) == ".txt" {
			rc, err := f.Open()
			if err != nil {
				c.String(http.StatusBadRequest, "Invalid input")
				return
			}
			defer rc.Close()

			_, err = io.Copy(&result, rc)
			if err != nil {
				c.String(http.StatusBadRequest, "Invalid input")
				return
			}
		}
	}

	c.String(http.StatusOK, result.String())
}