package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"net/http"
)

const maxSize = 10 << 20 // 10 MB

func main() {
	http.HandleFunc("/convert", convertHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func convertHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	if r.ContentLength > maxSize {
		http.Error(w, "File too large", http.StatusBadRequest)
		return
	}

	err := r.ParseMultipartForm(maxSize)
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}
	defer file.Close()

	var buffer bytes.Buffer
	zipReader, err := zip.NewReader(file, r.ContentLength)
	if err != nil {
		http.Error(w, "Invalid zip file", http.StatusBadRequest)
		return
	}

	for _, zf := range zipReader.File {
		if zf.FileInfo().IsDir() {
			continue
		}

		if isTextFile(zf.Name) {
			rc, err := zf.Open()
			if err != nil {
				http.Error(w, "Error reading zip file", http.StatusInternalServerError)
				return
			}
			defer rc.Close()

			_, err = io.Copy(&buffer, rc)
			if err != nil {
				http.Error(w, "Error reading file contents", http.StatusInternalServerError)
				return
			}
			buffer.WriteString("\n") // Separate files with a newline
		}
	}

	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write(buffer.Bytes())
}

func isTextFile(filename string) bool {
	return len(filename) > 4 && (filename[len(filename)-4:] == ".txt" || filename[len(filename)-4:] == ".csv")
}