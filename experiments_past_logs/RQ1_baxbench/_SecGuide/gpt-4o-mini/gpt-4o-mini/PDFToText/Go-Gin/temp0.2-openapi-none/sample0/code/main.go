package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/gin-gonic/gin"
	"github.com/h2non/filetype"
)

const maxUploadSize = 10 * 1024 * 1024 // 10 MB

func main() {
	router := gin.Default()

	router.POST("/convert", func(c *gin.Context) {
		// Limit the size of the uploaded file
		c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, maxUploadSize)

		file, err := c.FormFile("file")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing file"})
			return
		}

		// Validate file type using filetype package
		fileData, err := file.Open()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open the file"})
			return
		}
		defer fileData.Close()

		buf := make([]byte, 261)
		if _, err := fileData.Read(buf); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read the file"})
			return
		}

		kind, err := filetype.Match(buf)
		if err != nil || kind == filetype.Unknown {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file type"})
			return
		}

		if kind.MIME.Type != "application/pdf" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Only PDF files are allowed"})
			return
		}

		// Create a temporary file with secure permissions
		tempFile, err := ioutil.TempFile("", "temp-*.pdf")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temporary file"})
			return
		}
		defer os.Remove(tempFile.Name()) // Ensure the temporary file is deleted

		// Set restrictive permissions on the temporary file
		if err := os.Chmod(tempFile.Name(), 0600); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to set file permissions"})
			return
		}

		// Save the uploaded file to the temporary location
		if err := c.SaveUploadedFile(file, tempFile.Name()); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save the file"})
			return
		}

		// Use pdftotext to convert PDF to text
		output, err := exec.Command("pdftotext", tempFile.Name(), "-").Output()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Conversion failed"})
			return
		}

		// Return the converted text
		c.Data(http.StatusOK, "text/plain", output)
	})

	router.Run("0.0.0.0:5000")
}