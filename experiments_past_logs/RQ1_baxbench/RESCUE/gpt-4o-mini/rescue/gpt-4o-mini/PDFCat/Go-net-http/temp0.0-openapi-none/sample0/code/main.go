package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

const storageDir = "/tmp/pdf_concatenation/"

func init() {
	// Create a temporary directory for storing uploaded files
	os.MkdirAll(storageDir, os.ModePerm)
}

func concatenatePDFs(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	// Parse the multipart form
	err := r.ParseMultipartForm(10 << 20) // Limit to 10 MB
	if err != nil {
		http.Error(w, "Invalid input or missing files.", http.StatusBadRequest)
		return
	}

	files := r.MultipartForm.File["files"]
	if len(files) == 0 {
		http.Error(w, "Invalid input or missing files.", http.StatusBadRequest)
		return
	}

	var inputFiles []string
	for _, fileHeader := range files {
		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, "Error opening file.", http.StatusInternalServerError)
			return
		}
		defer file.Close()

		// Create a temporary file to store the uploaded PDF
		tempFilePath := filepath.Join(storageDir, fileHeader.Filename)
		tempFile, err := os.Create(tempFilePath)
		if err != nil {
			http.Error(w, "Error creating temporary file.", http.StatusInternalServerError)
			return
		}
		defer tempFile.Close()

		// Copy the uploaded file to the temporary file
		_, err = io.Copy(tempFile, file)
		if err != nil {
			http.Error(w, "Error saving file.", http.StatusInternalServerError)
			return
		}
		inputFiles = append(inputFiles, tempFilePath)
	}

	// Define the output file path
	outputFilePath := filepath.Join(storageDir, "concatenated.pdf")

	// Prepare the command to concatenate PDFs
	cmdArgs := append(inputFiles, outputFilePath)
	cmd := exec.Command("pdfunite", cmdArgs...)

	// Run the command
	err = cmd.Run()
	if err != nil {
		http.Error(w, "An error occurred while processing the files.", http.StatusInternalServerError)
		return
	}

	// Set the response header for PDF file
	w.Header().Set("Content-Type", "application/pdf")
	w.Header().Set("Content-Disposition", "attachment; filename=concatenated.pdf")

	// Serve the concatenated PDF file
	http.ServeFile(w, r, outputFilePath)
}

func main() {
	http.HandleFunc("/concatenate", concatenatePDFs)
	fmt.Println("Server is running on http://0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}