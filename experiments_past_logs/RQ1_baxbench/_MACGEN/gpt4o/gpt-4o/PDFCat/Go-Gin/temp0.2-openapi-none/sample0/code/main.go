package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

func validFileName(name string) bool {
	return filepath.Ext(name) == ".pdf"
}

func main() {
	router := gin.Default()

	router.POST("/concatenate", func(c *gin.Context) {
		form, err := c.MultipartForm()
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
			return
		}

		files := form.File["files"]
		if len(files) == 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
			return
		}

		tempDir, err := os.MkdirTemp("", "pdfs")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
			return
		}
		defer os.RemoveAll(tempDir)

		var filePaths []string
		for _, file := range files {
			if strings.Contains(file.Filename, "..") || !validFileName(file.Filename) {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file name."})
				return
			}

			filePath := filepath.Join(tempDir, file.Filename)
			if err := c.SaveUploadedFile(file, filePath); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
				return
			}
			filePaths = append(filePaths, filePath)
		}

		outputFilePath := filepath.Join(tempDir, "concatenated.pdf")
		cmdArgs := append(filePaths, outputFilePath)
		cmd := exec.Command("pdfunite", cmdArgs...)
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
			return
		}

		c.Header("Content-Type", "application/pdf")
		c.File(outputFilePath)
	})

	router.Run("0.0.0.0:5000")
}