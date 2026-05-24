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
)

func main() {
	http.HandleFunc("/convert", handleConvert)
	log.Println("Starting server on 0.0.0.0:5000...")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func handleConvert(w http.ResponseWriter, r *http.Request) {
	// Ensure the request method is POST
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Parse the multipart form
	err := r.ParseMultipartForm(10 << 20) // Limit upload size to 10MB
	if err != nil {
		http.Error(w, "Failed to parse form data", http.StatusBadRequest)
		return
	}

	// Retrieve the file from the form
	file, fileHeader, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "File is required", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Validate the file type (ensure it's a PDF)
	if filepath.Ext(fileHeader.Filename) != ".pdf" {
		http.Error(w, "Only PDF files are allowed", http.StatusBadRequest)
		return
	}

	// Create a temporary file to store the uploaded PDF
	tempFile, err := os.CreateTemp("", "uploaded-*.pdf")
	if err != nil {
		http.Error(w, "Failed to create temporary file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempFile.Name()) // Clean up the temporary file
	defer tempFile.Close()

	// Write the uploaded file to the temporary file
	_, err = io.Copy(tempFile, file)
	if err != nil {
		http.Error(w, "Failed to save uploaded file", http.StatusInternalServerError)
		return
	}

	// Use the `pdftotext` utility to extract text from the PDF
	outputBuffer := &bytes.Buffer{}
	cmd := exec.Command("pdftotext", tempFile.Name(), "-")
	cmd.Stdout = outputBuffer
	cmd.Stderr = outputBuffer

	err = cmd.Run()
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to convert PDF to text: %s", outputBuffer.String()), http.StatusInternalServerError)
		return
	}

	// Set the response headers and write the extracted text
	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	_, err = w.Write(outputBuffer.Bytes())
	if err != nil {
		log.Printf("Failed to write response: %v", err)
	}
}