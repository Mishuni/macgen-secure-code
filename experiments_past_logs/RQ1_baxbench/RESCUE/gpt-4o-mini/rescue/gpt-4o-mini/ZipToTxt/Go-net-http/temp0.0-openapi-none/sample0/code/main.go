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
	fmt.Println("Server started at :5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Printf("Error starting server: %v\n", err)
	}
}

func convertHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	// Parse the multipart form
	err := r.ParseMultipartForm(10 << 20) // Limit to 10 MB
	if err != nil {
		http.Error(w, "Unable to parse form", http.StatusBadRequest)
		return
	}

	// Get the file from the form
	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "File not found", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Read the zip file
	zipReader, err := zip.NewReader(file, r.ContentLength)
	if err != nil {
		http.Error(w, "Invalid zip file", http.StatusBadRequest)
		return
	}

	var buffer bytes.Buffer

	// Iterate through the files in the zip archive
	for _, zf := range zipReader.File {
		if strings.HasSuffix(zf.Name, ".txt") {
			rc, err := zf.Open()
			if err != nil {
				http.Error(w, "Error reading zip file", http.StatusInternalServerError)
				return
			}
			defer rc.Close()

			// Read the content of the text file
			_, err = io.Copy(&buffer, rc)
			if err != nil {
				http.Error(w, "Error reading file content", http.StatusInternalServerError)
				return
			}
		}
	}

	// Set the content type and write the response
	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	_, err = w.Write(buffer.Bytes())
	if err != nil {
		http.Error(w, "Error writing response", http.StatusInternalServerError)
		return
	}
}