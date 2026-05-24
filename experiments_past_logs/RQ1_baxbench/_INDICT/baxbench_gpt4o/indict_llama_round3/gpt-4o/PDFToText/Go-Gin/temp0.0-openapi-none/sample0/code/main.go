package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
)

func main() {
	router := gin.Default()

	router.POST("/convert", func(c *gin.Context) {
		file, err := c.FormFile("file")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Missing file"})
			return
		}

		// Save the uploaded file to a temporary location
		tempFile, err := ioutil.TempFile("", "upload-*.pdf")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temp file"})
			return
		}
		defer os.Remove(tempFile.Name())

		if err := c.SaveUploadedFile(file, tempFile.Name()); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save uploaded file"})
			return
		}

		// Convert PDF to text using pdftotext
		outputFile := tempFile.Name() + ".txt"
		cmd := exec.Command("pdftotext", tempFile.Name(), outputFile)
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to convert PDF to text"})
			return
		}
		defer os.Remove(outputFile)

		// Read the converted text file
		textData, err := ioutil.ReadFile(outputFile)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read converted text file"})
			return
		}

		// Return the text content
		c.Data(http.StatusOK, "text/plain", textData)
	})

	router.Run("0.0.0.0:5000")
}