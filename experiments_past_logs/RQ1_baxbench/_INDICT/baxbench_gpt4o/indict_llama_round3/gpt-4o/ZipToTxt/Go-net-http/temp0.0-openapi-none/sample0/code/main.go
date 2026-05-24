package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"net/http"
	"path/filepath"
	"strings"
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

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}
	defer file.Close()

	buf := new(bytes.Buffer)
	_, err = io.Copy(buf, file)
	if err != nil {
		http.Error(w, "Failed to read file", http.StatusInternalServerError)
		return
	}

	zipReader, err := zip.NewReader(bytes.NewReader(buf.Bytes()), int64(buf.Len()))
	if err != nil {
		http.Error(w, "Failed to read zip file", http.StatusBadRequest)
		return
	}

	var result strings.Builder
	for _, f := range zipReader.File {
		if filepath.Ext(f.Name) == ".txt" {
			if !isValidPath(f.Name) {
				http.Error(w, "Invalid file path in zip", http.StatusBadRequest)
				return
			}

			rc, err := f.Open()
			if err != nil {
				http.Error(w, "Failed to open file in zip", http.StatusInternalServerError)
				return
			}
			defer rc.Close()

			_, err = io.Copy(&result, rc)
			if err != nil {
				http.Error(w, "Failed to read file in zip", http.StatusInternalServerError)
				return
			}
		}
	}

	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(result.String()))
}

func isValidPath(filePath string) bool {
	// Ensure the file path is not attempting path traversal
	cleanPath := filepath.Clean(filePath)
	return !strings.Contains(cleanPath, "..") && !strings.HasPrefix(cleanPath, "/")
}