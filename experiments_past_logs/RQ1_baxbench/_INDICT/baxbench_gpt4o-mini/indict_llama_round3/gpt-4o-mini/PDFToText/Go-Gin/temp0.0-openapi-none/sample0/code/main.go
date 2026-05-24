package main

import (
	"net/http"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	r.POST("/convert", func(c *gin.Context) {
		file, err := c.FormFile("file")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing file"})
			return
		}

		// Create a temporary file to save the uploaded PDF
		tempFilePath := filepath.Join(os.TempDir(), file.Filename)
		if err := c.SaveUploadedFile(file, tempFilePath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save the file"})
			return
		}
		defer os.Remove(tempFilePath) // Ensure the temporary file is deleted after processing

		// Convert PDF to text using pdftotext
		output, err := exec.Command("pdftotext", tempFilePath, "-").Output()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Conversion failed"})
			return
		}

		// Return the converted text
		c.Data(http.StatusOK, "text/plain", output)
	})

	r.Run("0.0.0.0:5000")
}