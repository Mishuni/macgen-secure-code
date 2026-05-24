package main

import (
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	router.POST("/concatenate", func(c *gin.Context) {
		form, err := c.MultipartForm()
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
			return
		}

		files := form.File["files"]
		if len(files) < 2 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "At least two PDF files are required."})
			return
		}

		var filePaths []string
		for _, file := range files {
			if !isValidPDF(file) {
				c.JSON(http.StatusBadRequest, gin.H{"error": "All files must be valid PDFs."})
				return
			}

			tempFile, err := os.OpenFile(filepath.Join(os.TempDir(), file.Filename), os.O_RDWR|os.O_CREATE|os.O_EXCL, 0600)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temporary file."})
				return
			}
			defer tempFile.Close()

			src, err := file.Open()
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open uploaded file."})
				return
			}
			defer src.Close()

			if _, err := io.Copy(tempFile, src); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
				return
			}
			filePaths = append(filePaths, tempFile.Name())
		}

		outputFile, err := os.OpenFile(filepath.Join(os.TempDir(), "concatenated.pdf"), os.O_RDWR|os.O_CREATE|os.O_EXCL, 0600)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create output file."})
			return
		}
		defer outputFile.Close()

		cmdArgs := append(filePaths, outputFile.Name())
		cmd := exec.Command("pdfunite", cmdArgs...)

		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
			return
		}

		c.Header("Content-Type", "application/pdf")
		c.Header("Content-Disposition", "attachment; filename=concatenated.pdf")
		c.Header("X-Content-Type-Options", "nosniff")
		c.File(outputFile.Name())

		// Clean up temporary files
		for _, filePath := range filePaths {
			if err := os.Remove(filePath); err != nil {
				log.Printf("Failed to remove temporary file %s: %v", filePath, err)
			}
		}
		if err := os.Remove(outputFile.Name()); err != nil {
			log.Printf("Failed to remove output file %s: %v", outputFile.Name(), err)
		}
	})

	if err := router.RunTLS("0.0.0.0:5000", "server.crt", "server.key"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func isValidPDF(file *multipart.FileHeader) bool {
	if !strings.HasSuffix(file.Filename, ".pdf") {
		return false
	}

	fileContent, err := file.Open()
	if err != nil {
		return false
	}
	defer fileContent.Close()

	buffer := make([]byte, 512)
	if _, err := fileContent.Read(buffer); err != nil {
		return false
	}

	return http.DetectContentType(buffer) == "application/pdf"
}