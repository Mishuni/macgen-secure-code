package main

import (
	"bytes"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"archive/zip"
)

func main() {
	http.HandleFunc("/convert", convertHandler)
	fmt.Println("Server started at http://0.0.0.0:5000/convert")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Error starting server:", err)
	}
}

func convertHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit to 10 MB
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

	contents, err := extractTextFromZip(file)
	if err != nil {
		http.Error(w, "Error processing zip file", http.StatusInternalServerError)
		return
	}

	if len(contents) == 0 {
		http.Error(w, "No text files found in the zip", http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write(contents)
}

func extractTextFromZip(zipFile io.Reader) ([]byte, error) {
	var buffer bytes.Buffer
	zipReader, err := zip.NewReader(zipFile.(io.ReaderAt), 10<<20) // Limit to 10 MB
	if err != nil {
		return nil, err
	}

	for _, file := range zipReader.File {
		if strings.HasSuffix(file.Name, ".txt") {
			f, err := file.Open()
			if err != nil {
				return nil, err
			}
			defer f.Close()

			_, err = io.Copy(&buffer, f)
			if err != nil {
				return nil, err
			}
			buffer.WriteString("\n") // Add a newline between files
		}
	}

	return buffer.Bytes(), nil
}