package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os/exec"
	"path/filepath"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()
	router.POST("/convert", convertPDF)
	router.Run("0.0.0.0:5000")
}

func convertPDF(c *gin.Context) {
	// Validate file upload
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing file"})
		return
	}

	// Validate file type
	if filepath.Ext(file.Filename) != ".pdf" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "File must be a PDF"})
		return
	}

	// Save the uploaded file to a temporary location
	tempFilePath := "./" + file.Filename
	if err := c.SaveUploadedFile(file, tempFilePath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}
	defer func() {
		_ = exec.Command("rm", tempFilePath).Run() // Clean up the temporary file
	}()

	// Execute pdftotext command
	output, err := exec.Command("pdftotext", tempFilePath, "-").Output()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Conversion failed"})
		return
	}

	// Return the extracted text
	c.Data(http.StatusOK, "text/plain", output)
}