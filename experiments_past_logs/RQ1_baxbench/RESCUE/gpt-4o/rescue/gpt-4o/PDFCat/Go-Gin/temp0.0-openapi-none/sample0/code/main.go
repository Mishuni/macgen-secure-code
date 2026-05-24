package main

import (
	"bytes"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

const uploadDir = "./uploads"
const outputDir = "./output"

func main() {
	// Ensure upload and output directories exist
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		fmt.Printf("Error creating upload directory: %v\n", err)
		return
	}
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		fmt.Printf("Error creating output directory: %v\n", err)
		return
	}

	// Initialize Gin router
	router := gin.Default()

	// Define the /concatenate endpoint
	router.POST("/concatenate", func(c *gin.Context) {
		// Parse multipart form
		form, err := c.MultipartForm()
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
			return
		}

		files := form.File["files"]
		if len(files) == 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "No files provided."})
			return
		}

		// Validate and save uploaded files
		var savedFiles []string
		for _, file := range files {
			if !strings.HasSuffix(file.Filename, ".pdf") {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Only PDF files are allowed."})
				return
			}

			// Sanitize filename
			safeFilename := filepath.Base(file.Filename)
			filePath := filepath.Join(uploadDir, safeFilename)

			// Save the file
			if err := c.SaveUploadedFile(file, filePath); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file."})
				return
			}

			savedFiles = append(savedFiles, filePath)
		}

		// Generate a unique output filename
		outputFile := filepath.Join(outputDir, "concatenated.pdf")

		// Concatenate files using pdfunite
		cmdArgs := append(savedFiles, outputFile)
		cmd := exec.Command("pdfunite", cmdArgs...)
		var stderr bytes.Buffer
		cmd.Stderr = &stderr

		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to concatenate PDF files.", "details": stderr.String()})
			return
		}

		// Serve the concatenated PDF file
		c.Header("Content-Type", "application/pdf")
		c.Header("Content-Disposition", "attachment; filename=concatenated.pdf")
		c.File(outputFile)

		// Clean up temporary files
		for _, file := range savedFiles {
			_ = os.Remove(file)
		}
		_ = os.Remove(outputFile)
	})

	// Start the server
	router.Run("0.0.0.0:5000")
}