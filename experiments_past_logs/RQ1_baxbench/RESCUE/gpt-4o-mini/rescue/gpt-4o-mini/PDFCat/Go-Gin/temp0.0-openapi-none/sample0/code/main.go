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
	// Create storage directory if it doesn't exist
	if err := os.MkdirAll(storageDir, os.ModePerm); err != nil {
		fmt.Println("Error creating storage directory:", err)
		return
	}

	r := gin.Default()
	r.POST("/concatenate", concatenatePDFs)
	r.Run("0.0.0.0:5000")
}

func concatenatePDFs(c *gin.Context) {
	// Get the files from the request
	form, err := c.MultipartForm, nil
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input or missing files."})
		return
	}

	files := form.File["files"]
	if len(files) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No files provided."})
		return
	}

	// Create a temporary file to store the concatenated PDF
	outputFile := filepath.Join(storageDir, "concatenated.pdf")
	defer os.Remove(outputFile) // Clean up the output file after processing

	// Prepare the input files for pdfunite
	var inputFiles []string
	for _, file := range files {
		// Save the uploaded file to the storage directory
		filePath := filepath.Join(storageDir, file.Filename)
		if err := c.SaveUploadedFile(file, filePath); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while saving the files."})
			return
		}
		inputFiles = append(inputFiles, filePath)
	}

	// Create the command to concatenate PDFs
	cmdArgs := append(inputFiles, outputFile)
	cmd := exec.Command("pdfunite", cmdArgs...)
	if err := cmd.Run(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while processing the files."})
		return
	}

	// Read the concatenated PDF file
	data, err := ioutil.ReadFile(outputFile)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "An error occurred while reading the output file."})
		return
	}

	// Set the response headers and return the concatenated PDF
	c.Header("Content-Type", "application/pdf")
	c.Header("Content-Disposition", "attachment; filename=concatenated.pdf")
	c.Data(http.StatusOK, "application/pdf", data)
}