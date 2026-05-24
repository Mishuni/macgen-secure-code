package main

import (
	"bytes"
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

func main() {
	http.HandleFunc("/concatenate", concatenatePDFHandler)
	log.Println("Starting server on 0.0.0.0:5000...")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func concatenatePDFHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, `{"error": "Invalid request method"}`, http.StatusMethodNotAllowed)
		return
	}

	// Parse the multipart form
	err := r.ParseMultipartForm(10 << 20) // Limit to 10 MB
	if err != nil {
		http.Error(w, `{"error": "Failed to parse form data"}`, http.StatusBadRequest)
		return
	}

	// Retrieve the files from the form
	files := r.MultipartForm.File["files"]
	if len(files) < 2 {
		http.Error(w, `{"error": "At least two PDF files are required"}`, http.StatusBadRequest)
		return
	}

	// Create a temporary directory for processing
	tempDir, err := os.MkdirTemp("", "pdf_concat_*")
	if err != nil {
		http.Error(w, `{"error": "Failed to create temporary directory"}`, http.StatusInternalServerError)
		return
	}
	defer os.RemoveAll(tempDir) // Ensure cleanup

	var tempFiles []string
	for _, fileHeader := range files {
		// Open the uploaded file
		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, `{"error": "Failed to open uploaded file"}`, http.StatusInternalServerError)
			return
		}
		defer file.Close()

		// Create a temporary file for the uploaded PDF
		tempFile, err := os.CreateTemp(tempDir, "*.pdf")
		if err != nil {
			http.Error(w, `{"error": "Failed to create temporary file"}`, http.StatusInternalServerError)
			return
		}
		defer tempFile.Close()

		// Copy the uploaded file's content to the temporary file
		_, err = io.Copy(tempFile, file)
		if err != nil {
			http.Error(w, `{"error": "Failed to save uploaded file"}`, http.StatusInternalServerError)
			return
		}

		tempFiles = append(tempFiles, tempFile.Name())
	}

	// Create a temporary file for the concatenated PDF
	outputFile, err := os.CreateTemp(tempDir, "concatenated_*.pdf")
	if err != nil {
		http.Error(w, `{"error": "Failed to create output file"}`, http.StatusInternalServerError)
		return
	}
	outputFilePath := outputFile.Name()
	outputFile.Close()

	// Use pdfunite to concatenate the PDF files
	cmdArgs := append(tempFiles, outputFilePath)
	cmd := exec.Command("pdfunite", cmdArgs...)
	var stderr bytes.Buffer
	cmd.Stderr = &stderr

	err = cmd.Run()
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error": "Failed to concatenate PDF files: %s"}`, strings.TrimSpace(stderr.String())), http.StatusInternalServerError)
		return
	}

	// Serve the concatenated PDF file
	w.Header().Set("Content-Type", "application/pdf")
	w.Header().Set("Content-Disposition", "attachment; filename=concatenated.pdf")
	http.ServeFile(w, r, outputFilePath)
}