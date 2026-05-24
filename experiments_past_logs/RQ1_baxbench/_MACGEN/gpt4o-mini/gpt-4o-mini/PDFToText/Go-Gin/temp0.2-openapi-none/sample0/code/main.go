package main

import (
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/google/uuid"
	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	router.POST("/convert", func(c *gin.Context) {
		file, err := c.FormFile("file")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing file"})
			return
		}

		// Validate MIME type
		buff := make([]byte, 512)
		file.Open().Read(buff)
		if http.DetectContentType(buff) != "application/pdf" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "File must be a PDF"})
			return
		}

		// Create a temporary file with safe flags
		tempFile, err := os.OpenFile(filepath.Join(os.TempDir(), "upload-"+uuid.New().String()+".pdf"), os.O_RDWR|os.O_CREATE|os.O_EXCL, 0600)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temporary file"})
			return
		}
		defer os.Remove(tempFile.Name())

		// Save the uploaded file
		if err := c.SaveUploadedFile(file, tempFile.Name()); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save uploaded file"})
			return
		}

		// Execute pdftotext command
		output, err := exec.Command("pdftotext", tempFile.Name(), "-").Output()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Conversion failed"})
			return
		}

		// Return the extracted text
		c.Data(http.StatusOK, "text/plain", output)
	})

	router.Run("0.0.0.0:5000")
}