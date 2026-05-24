package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

const maxUploadSize = 10 * 1024 * 1024 // 10 MB

func main() {
	http.HandleFunc("/convert", convertHandler)
	fmt.Println("Server started at :5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}

func convertHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	// Limit the size of the uploaded file
	r.ParseMultipartForm(maxUploadSize)

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Missing file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Create a temporary file to save the uploaded PDF
	tempFile, err := os.CreateTemp("", "upload-*.pdf")
	if err != nil {
		http.Error(w, "Unable to create temporary file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempFile.Name()) // Clean up the temp file

	// Save the uploaded file to the temporary file
	if _, err := io.Copy(tempFile, file); err != nil {
		http.Error(w, "Failed to save file", http.StatusInternalServerError)
		return
	}

	// Convert PDF to text using pdftotext
	output, err := exec.Command("pdftotext", tempFile.Name(), "-").Output()
	if err != nil {
		http.Error(w, "Failed to convert PDF to text", http.StatusInternalServerError)
		return
	}

	// Set the response header and write the output
	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write(output)
}