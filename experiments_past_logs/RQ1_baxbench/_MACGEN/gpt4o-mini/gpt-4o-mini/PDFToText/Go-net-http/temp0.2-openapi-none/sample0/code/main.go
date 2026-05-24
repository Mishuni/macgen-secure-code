package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
)

func main() {
	http.HandleFunc("/convert", convertPDFToText)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func convertPDFToText(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "Bad Request - Invalid input", http.StatusBadRequest)
		return
	}

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Bad Request - Missing file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Validate file type
	buff := make([]byte, 512)
	if _, err := file.Read(buff); err != nil || http.DetectContentType(buff) != "application/pdf" {
		http.Error(w, "Invalid file type", http.StatusBadRequest)
		return
	}

	// Create a temporary file
	tempFile, err := os.CreateTemp("", "pdf-*.pdf")
	if err != nil {
		http.Error(w, "Internal Server Error - Unable to create temp file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempFile.Name()) // Clean up the temp file

	// Write the uploaded file to the temp file
	if _, err := io.Copy(tempFile, file); err != nil {
		http.Error(w, "Internal Server Error - Unable to save file", http.StatusInternalServerError)
		return
	}

	// Extract text from PDF
	text, err := extractTextFromPDF(tempFile.Name())
	if err != nil {
		http.Error(w, "Internal Server Error - Conversion failed", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/plain")
	w.Write([]byte(text))
}

func extractTextFromPDF(pdfPath string) (string, error) {
	cmd := exec.Command("pdftotext", pdfPath, "-")
	output, err := cmd.Output()
	if err != nil {
		return "", err
	}
	return string(output), nil
}