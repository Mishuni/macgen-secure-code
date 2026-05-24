package main

import (
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	r.POST("/concatenate", func(c *gin.Context) {
		// Parse the multipart form
		if err := c.Request.ParseMultipartForm(0); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
			return
		}

		// Retrieve the files
		files := c.Request.MultipartForm.File["files"]
		if len(files) == 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
			return
		}

		// Create temporary files to store the uploaded PDFs
		var inputFiles []string
		for _, fileHeader := range files {
			file, err := fileHeader.Open()
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
				return
			}

			tempFile, err := os.CreateTemp("", "*.pdf")
			if err != nil {
				file.Close()
				c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
				return
			}

			if _, err := io.Copy(tempFile, file); err != nil {
				tempFile.Close()
				file.Close()
				c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
				return
			}
			file.Close() // Close the uploaded file immediately after copying
			tempFile.Close() // Close the temp file after copying
			inputFiles = append(inputFiles, tempFile.Name())
		}

		// Create a temporary output file for the concatenated PDF
		outputFile, err := os.CreateTemp("", "concatenated-*.pdf")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
			return
		}
		defer os.Remove(outputFile.Name()) // Clean up the output file

		// Prepare the command to concatenate PDFs
		args := append(inputFiles, outputFile.Name())
		cmd := exec.Command("pdfunite", args...)
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
			return
		}

		// Serve the concatenated PDF
		c.Header("Content-Type", "application/pdf")
		c.File(outputFile.Name())
	})

	r.Run("0.0.0.0:5000")
}