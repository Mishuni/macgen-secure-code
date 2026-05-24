package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
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
	form, err := c.MultipartForm()
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
		return
	}

	files := form.File["files"]
	if len(files) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No files uploaded."})
		return
	}

	tempDir, err := os.MkdirTemp("", "pdf_concat")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temporary directory."})
		return
	}
	defer os.RemoveAll(tempDir)

	var inputFilePaths []string
	for _, file := range files {
		if !isValidPDF(file.Filename) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file type."})
			return
		}

		filePath := filepath.Join(tempDir, file.Filename)
		if err := c.SaveUploadedFile(file, filePath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save uploaded file."})
			return
		}
		inputFilePaths = append(inputFilePaths, filePath)
	}

	outputFilePath := filepath.Join(tempDir, "concatenated.pdf")
	cmdArgs := append(inputFilePaths, outputFilePath)
	cmd := exec.Command("pdfunite", cmdArgs...)

	if err := cmd.Run(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to concatenate PDF files."})
		return
	}

	c.File(outputFilePath)
}

func isValidPDF(filename string) bool {
	ext := filepath.Ext(filename)
	return ext == ".pdf"
}