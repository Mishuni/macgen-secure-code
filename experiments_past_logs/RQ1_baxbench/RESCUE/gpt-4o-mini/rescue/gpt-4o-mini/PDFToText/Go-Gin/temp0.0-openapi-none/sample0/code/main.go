package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/gin-gonic/gin"
)

const storageDir = "./uploads/"

func main() {
	// Create the uploads directory if it doesn't exist
	if err := os.MkdirAll(storageDir, os.ModePerm); err != nil {
		fmt.Println("Failed to create upload directory:", err)
		return
	}

	r := gin.Default()
	r.POST("/convert", convertPDFToText)
	r.Run("0.0.0.0:5000")
}

func convertPDFToText(c *gin.Context) {
	// Validate and get the file from the request
	file, err := c.FormFile("file")
	if err != nil || file == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing file"})
		return
	}

	// Sanitize the file name and save the file
	filePath := filepath.Join(storageDir, filepath.Base(file.Filename))
	if err := c.SaveUploadedFile(file, filePath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}
	defer os.Remove(filePath) // Clean up the file after processing

	// Convert PDF to text using pdftotext
	textFilePath := filePath + ".txt"
	cmd := exec.Command("pdftotext", filePath, textFilePath)
	if err := cmd.Run(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Conversion failed"})
		return
	}
	defer os.Remove(textFilePath) // Clean up the text file after processing

	// Read the converted text
	text, err := ioutil.ReadFile(textFilePath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read converted text"})
		return
	}

	// Return the converted text
	c.Data(http.StatusOK, "text/plain", text)
}