package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

const maxUploadSize = 10 << 20 // 10 MB

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
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Create a zip reader directly from the file
	zipReader, err := zip.NewReader(file, maxUploadSize)
	if err != nil {
		http.Error(w, "Invalid zip file", http.StatusBadRequest)
		return
	}

	var buffer bytes.Buffer
	for _, zf := range zipReader.File {
		if !isTextFile(zf.Name) {
			http.Error(w, "Unsupported file type: "+zf.Name, http.StatusUnsupportedMediaType)
			return
		}

		// Sanitize the file name to prevent path traversal
		if !isValidFileName(zf.Name) {
			http.Error(w, "Invalid file name: "+zf.Name, http.StatusBadRequest)
			return
		}

		rc, err := zf.Open()
		if err != nil {
			http.Error(w, "Failed to open file in zip", http.StatusInternalServerError)
			return
		}

		// Use a buffer to read the file content
		if _, err := io.Copy(&buffer, rc); err != nil {
			rc.Close()
			http.Error(w, "Failed to read file in zip", http.StatusInternalServerError)
			return
		}
		rc.Close()
	}

	// Set security-related headers
	w.Header().Set("Content-Type", "text/plain")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.Header().Set("X-Frame-Options", "DENY")
	w.Header().Set("Content-Security-Policy", "default-src 'self';")
	w.Header().Set("X-XSS-Protection", "1; mode=block")
	w.Header().Set("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
	w.Header().Set("Referrer-Policy", "no-referrer")
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write(buffer.Bytes())
}

func isTextFile(name string) bool {
	ext := strings.ToLower(filepath.Ext(name))
	return ext == ".txt" || ext == ".csv" || ext == ".log" // Add more text file types if needed
}

func isValidFileName(name string) bool {
	// Check for invalid characters and path traversal
	if strings.Contains(name, "..") || strings.Contains(name, "/") || strings.Contains(name, "\\") {
		return false
	}
	return true
}