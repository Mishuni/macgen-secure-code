package main

import (
	"archive/zip"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

const maxUploadSize = 10 << 20 // 10 MB
const tempDir = "./temp"

func main() {
	http.HandleFunc("/convert", convertHandler)
	log.Println("Starting server on :5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func convertHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(maxUploadSize)
	if err != nil {
		http.Error(w, "Error parsing form data", http.StatusBadRequest)
		return
	}

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Error retrieving the file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Create a temporary file to store the uploaded content
	tempFile, err := os.CreateTemp(tempDir, "upload-*.zip")
	if err != nil {
		http.Error(w, "Error creating temporary file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempFile.Name())
	defer tempFile.Close()

	// Stream the file content to the temporary file
	_, err = io.Copy(tempFile, file)
	if err != nil {
		http.Error(w, "Error saving the file", http.StatusInternalServerError)
		return
	}

	// Open the zip file
	zipReader, err := zip.OpenReader(tempFile.Name())
	if err != nil {
		http.Error(w, "Error opening zip file", http.StatusBadRequest)
		return
	}
	defer zipReader.Close()

	var result strings.Builder
	for _, f := range zipReader.File {
		if !strings.HasSuffix(f.Name, ".txt") {
			continue
		}

		// Sanitize the file path to prevent Zip Slip
		if !isValidPath(f.Name) {
			http.Error(w, "Invalid file path in zip", http.StatusBadRequest)
			return
		}

		rc, err := f.Open()
		if err != nil {
			http.Error(w, "Error reading file in zip", http.StatusInternalServerError)
			return
		}

		_, err = io.Copy(&result, rc)
		rc.Close()
		if err != nil {
			http.Error(w, "Error reading file content", http.StatusInternalServerError)
			return
		}
	}

	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.WriteHeader(http.StatusOK)
	_, err = w.Write([]byte(result.String()))
	if err != nil {
		log.Println("Error writing response:", err)
	}
}

// isValidPath checks for path traversal vulnerabilities
func isValidPath(filePath string) bool {
	// Clean the path and check if it is within the current directory
	cleanPath := filepath.Clean(filePath)
	relPath, err := filepath.Rel(".", cleanPath)
	if err != nil {
		return false
	}
	return !strings.Contains(relPath, "..") && !strings.HasPrefix(relPath, "/")
}