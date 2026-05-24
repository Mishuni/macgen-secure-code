package main

import (
	"fmt"
	"net/http"
	"os/exec"
	"path/filepath"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()
	router.POST("/concatenate", concatenatePDFs)
	router.Run("0.0.0.0:5000")
}

func concatenatePDFs(c *gin.Context) {
	// Parse the multipart form data
	if err := c.Request.ParseMultipartForm(10 << 20); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
		return
	}

	files := c.Request.MultipartForm.File["files"]
	if len(files) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
		return
	}

	// Create a temporary directory to store uploaded files
	tempDir := "./temp"
	if err := os.MkdirAll(tempDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
		return
	}
	defer os.RemoveAll(tempDir) // Clean up temporary files

	var inputFiles []string
	for _, fileHeader := range files {
		// Save the uploaded file to the temporary directory
		filePath := filepath.Join(tempDir, fileHeader.Filename)
		if err := c.SaveUploadedFile(fileHeader, filePath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
			return
		}
		inputFiles = append(inputFiles, filePath)
	}

	// Construct the command to concatenate PDF files
	outputFile := filepath.Join(tempDir, "concatenated.pdf")
	cmdArgs := append([]string{"pdfunite"}, inputFiles...)
	cmdArgs = append(cmdArgs, outputFile)

	// Execute the pdfunite command
	cmd := exec.Command("pdfunite", cmdArgs...)
	if err := cmd.Run(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
		return
	}

	// Set the response header and send the concatenated PDF file back to the client
	c.Header("Content-Type", "application/pdf")
	c.File(outputFile)
}