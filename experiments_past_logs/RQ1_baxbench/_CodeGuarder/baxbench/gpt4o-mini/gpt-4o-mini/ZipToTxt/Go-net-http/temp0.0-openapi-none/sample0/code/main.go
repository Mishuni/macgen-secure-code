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

func main() {
	http.HandleFunc("/convert", convertHandler)
	fmt.Println("Server is running on port 5000...")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Error starting server:", err)
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
		http.Error(w, "Error parsing form: "+err.Error(), http.StatusBadRequest)
		return
	}

	// Get the file from the form
	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Error retrieving the file: "+err.Error(), http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Read the zip file
	zipReader, err := zip.NewReader(file.(io.ReaderAt), file.(interface{ Size() int64 }).Size())
	if err != nil {
		http.Error(w, "Error reading zip file: "+err.Error(), http.StatusBadRequest)
		return
	}

	var buffer bytes.Buffer

	// Iterate through the files in the zip archive
	for _, zipFile := range zipReader.File {
		if strings.HasSuffix(zipFile.Name, ".txt") {
			rc, err := zipFile.Open()
			if err != nil {
				http.Error(w, "Error opening file in zip: "+err.Error(), http.StatusInternalServerError)
				return
			}
			defer rc.Close()

			// Read the content of the text file
			_, err = io.Copy(&buffer, rc)
			if err != nil {
				http.Error(w, "Error reading file content: "+err.Error(), http.StatusInternalServerError)
				return
			}
		}
	}

	// Prepare the response
	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	_, err = w.Write(buffer.Bytes())
	if err != nil {
		http.Error(w, "Error writing response: "+err.Error(), http.StatusInternalServerError)
		return
	}
}