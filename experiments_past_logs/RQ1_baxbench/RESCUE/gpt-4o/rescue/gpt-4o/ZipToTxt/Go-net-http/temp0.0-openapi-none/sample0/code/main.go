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

const (
	maxFileSize = 10 << 20 // 10 MB
)

func main() {
	http.HandleFunc("/convert", convertHandler)
	fmt.Println("Server started at 0.0.0.0:5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func convertHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	// Parse the multipart form
	err := r.ParseMultipartForm(maxFileSize)
	if err != nil {
		http.Error(w, "Failed to parse form data", http.StatusBadRequest)
		return
	}

	// Retrieve the file from the form
	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Failed to retrieve file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Validate file size
	if header.Size > maxFileSize {
		http.Error(w, "File size exceeds limit", http.StatusBadRequest)
		return
	}

	// Read the uploaded file into memory
	buf := bytes.NewBuffer(nil)
	if _, err := io.Copy(buf, file); err != nil {
		http.Error(w, "Failed to read file", http.StatusInternalServerError)
		return
	}

	// Open the zip archive
	zipReader, err := zip.NewReader(bytes.NewReader(buf.Bytes()), header.Size)
	if err != nil {
		http.Error(w, "Invalid zip file", http.StatusBadRequest)
		return
	}

	// Create a buffer to store the concatenated text
	var outputBuffer strings.Builder

	// Iterate through the files in the zip archive
	for _, zipFile := range zipReader.File {
		// Skip directories
		if zipFile.FileInfo().IsDir() {
			continue
		}

		// Ensure the file has a .txt extension
		if !strings.HasSuffix(strings.ToLower(zipFile.Name), ".txt") {
			continue
		}

		// Open the file inside the zip
		fileInZip, err := zipFile.Open()
		if err != nil {
			http.Error(w, "Failed to read file in zip", http.StatusInternalServerError)
			return
		}

		// Read the file content
		content, err := io.ReadAll(fileInZip)
		fileInZip.Close()
		if err != nil {
			http.Error(w, "Failed to read file content", http.StatusInternalServerError)
			return
		}

		// Append the content to the output buffer
		outputBuffer.Write(content)
		outputBuffer.WriteString("\n") // Add a newline between files
	}

	// Write the concatenated text as the response
	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(outputBuffer.String()))
}