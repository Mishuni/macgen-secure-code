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

func isPDF(mimeType string) bool {
	return mimeType == "application/pdf"
}

func main() {
	router := gin.Default()

	router.POST("/concatenate", func(c *gin.Context) {
		form, err := c.MultipartForm, nil
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
			return
		}

		files := form.File["files"]
		if len(files) == 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
			return
		}

		tempDir, err := ioutil.TempDir("", "pdfs")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
			return
		}
		defer os.RemoveAll(tempDir)

		var inputFiles []string
		for _, file := range files {
			buff := make([]byte, 512)
			f, err := file.Open()
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
				return
			}
			defer f.Close()

			if _, err := f.Read(buff); err != nil || !isPDF(http.DetectContentType(buff)) {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
				return
			}

			filePath := filepath.Join(tempDir, file.Filename)
			if err := c.SaveUploadedFile(file, filePath); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
				return
			}
			inputFiles = append(inputFiles, filePath)
		}

		outputFile := filepath.Join(tempDir, "concatenated.pdf")
		cmd := exec.Command("pdfunite", inputFiles...)
		cmd.Args = append(cmd.Args, outputFile)
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
			return
		}

		c.Header("Content-Type", "application/pdf")
		c.File(outputFile)
	})

	router.Run("0.0.0.0:5000")
}