package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/google/uuid"
)

func main() {
	router := gin.Default()

	router.POST("/concatenate", func(c *gin.Context) {
		form, err := c.MultipartForm()
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
			return
		}

		files := form.File["files"]
		if len(files) < 2 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "At least two files are required."})
			return
		}

		var filePaths []string
		for _, file := range files {
			uniqueFileName := uuid.New().String() + filepath.Ext(file.Filename)
			filePath := filepath.Join("/tmp", uniqueFileName)
			if err := c.SaveUploadedFile(file, filePath); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
				return
			}
			filePaths = append(filePaths, filePath)
		}

		outputFilePath := "/tmp/concatenated.pdf"
		cmdArgs := append(filePaths, outputFilePath)
		cmd := exec.Command("pdfunite", cmdArgs...)
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
			return
		}

		outputFile, err := os.Open(outputFilePath)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
			return
		}
		defer outputFile.Close()

		c.Header("Content-Disposition", "attachment; filename=concatenated.pdf")
		c.Header("Content-Type", "application/pdf")
		c.Status(http.StatusOK)
		io.Copy(c.Writer, outputFile)

		// Clean up temporary files
		for _, filePath := range filePaths {
			os.Remove(filePath)
		}
		os.Remove(outputFilePath)
	})

	router.Run("0.0.0.0:5000")
}