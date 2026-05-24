package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/google/uuid"
)

func main() {
	http.HandleFunc("/concatenate", concatenateHandler)
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func concatenateHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit upload size to 10 MB
	if err != nil {
		http.Error(w, "Error parsing form data", http.StatusBadRequest)
		return
	}

	files := r.MultipartForm.File["files"]
	if len(files) == 0 {
		http.Error(w, "No files uploaded", http.StatusBadRequest)
		return
	}

	tempDir, err := os.MkdirTemp("", "pdfconcat")
	if err != nil {
		http.Error(w, "Error creating temporary directory", http.StatusInternalServerError)
		return
	}
	defer os.RemoveAll(tempDir)

	var filePaths []string
	for _, fileHeader := range files {
		if fileHeader.Filename == "" || strings.Contains(fileHeader.Filename, "..") {
			http.Error(w, "Invalid file name", http.StatusBadRequest)
			return
		}

		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, "Error opening file", http.StatusInternalServerError)
			return
		}
		defer file.Close()

		tempFilePath := filepath.Join(tempDir, uuid.New().String()+".pdf")
		tempFile, err := os.Create(tempFilePath)
		if err != nil {
			http.Error(w, "Error creating temporary file", http.StatusInternalServerError)
			return
		}

		_, err = io.Copy(tempFile, file)
		tempFile.Close()
		if err != nil {
			http.Error(w, "Error saving file", http.StatusInternalServerError)
			return
		}

		filePaths = append(filePaths, tempFilePath)
	}

	outputFilePath := filepath.Join(tempDir, "concatenated.pdf")
	cmdArgs := append(filePaths, outputFilePath)
	cmd := exec.Command("pdfunite", cmdArgs...)
	err = cmd.Run()
	if err != nil {
		http.Error(w, "Error concatenating PDF files", http.StatusInternalServerError)
		return
	}

	outputFile, err := os.Open(outputFilePath)
	if err != nil {
		http.Error(w, "Error opening concatenated PDF", http.StatusInternalServerError)
		return
	}
	defer outputFile.Close()

	w.Header().Set("Content-Type", "application/pdf")
	w.Header().Set("Content-Disposition", "attachment; filename=concatenated.pdf")
	_, err = io.Copy(w, outputFile)
	if err != nil {
		http.Error(w, "Error sending concatenated PDF", http.StatusInternalServerError)
		return
	}
}