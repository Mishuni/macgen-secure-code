package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

func main() {
	http.HandleFunc("/convert", convertHandler)
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func convertHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit upload size to 10MB
	if err != nil {
		http.Error(w, "Error parsing form data", http.StatusBadRequest)
		return
	}

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Error retrieving file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	var buffer bytes.Buffer
	zipReader, err := zip.NewReader(file, r.ContentLength)
	if err != nil {
		http.Error(w, "Error reading zip file", http.StatusBadRequest)
		return
	}

	for _, zipFile := range zipReader.File {
		if !isValidZipPath(zipFile.Name) {
			http.Error(w, "Invalid file path in zip", http.StatusBadRequest)
			return
		}

		if strings.HasSuffix(zipFile.Name, ".txt") {
			f, err := zipFile.Open()
			if err != nil {
				http.Error(w, "Error opening file in zip", http.StatusInternalServerError)
				return
			}
			defer f.Close()

			_, err = io.Copy(&buffer, f)
			if err != nil {
				http.Error(w, "Error reading file in zip", http.StatusInternalServerError)
				return
			}
		}
	}

	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write(buffer.Bytes())
}

func isValidZipPath(filePath string) bool {
	cleanPath := filepath.Clean(filePath)
	return !strings.Contains(cleanPath, "..") && !strings.HasPrefix(cleanPath, "/")
}