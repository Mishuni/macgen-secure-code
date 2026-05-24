package main

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

// isValidPDF checks if the file has a valid PDF extension and MIME type
func isValidPDF(fileName string) bool {
	// Check if the file extension is .pdf
	return strings.HasSuffix(strings.ToLower(fileName), ".pdf")
}

// sanitizeFileName sanitizes the file name to prevent path traversal attacks
func sanitizeFileName(fileName string) string {
	return filepath.Base(fileName)
}

func main() {
	r := gin.Default()

	r.POST("/concatenate", func(c *gin.Context) {
		// Get the files from the form
		form, err := c.MultipartForm, nil
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
			return
		}

		files := form.File["files"]
		if len(files) == 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
			return
		}

		// Create temporary files to store the uploaded PDFs
		var pdfFiles []string
		for _, file := range files {
			if !isValidPDF(file.Filename) {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file type. Only PDF files are allowed."})
				return
			}

			// Sanitize the file name
			sanitizedFileName := sanitizeFileName(file.Filename)

			tempFile, err := os.CreateTemp("", sanitizedFileName)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
				return
			}
			defer os.Remove(tempFile.Name()) // Clean up the temp file after processing

			if err := c.SaveUploadedFile(file, tempFile.Name()); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
				return
			}
			pdfFiles = append(pdfFiles, tempFile.Name())
		}

		// Create a temporary output file for the concatenated PDF
		outputFile, err := os.CreateTemp("", "concatenated_*.pdf")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
			return
		}
		defer os.Remove(outputFile.Name()) // Clean up the output file after processing

		// Prepare the command to concatenate PDFs
		args := append(pdfFiles, outputFile.Name())
		cmd := exec.Command("pdfunite", args...)
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
			return
		}

		// Set the response headers and send the concatenated PDF
		c.Header("Content-Type", "application/pdf")
		c.Header("Content-Disposition", fmt.Sprintf("attachment; filename=%s", filepath.Base(outputFile.Name())))
		c.File(outputFile.Name())
	})

	r.Run("0.0.0.0:5000")
}