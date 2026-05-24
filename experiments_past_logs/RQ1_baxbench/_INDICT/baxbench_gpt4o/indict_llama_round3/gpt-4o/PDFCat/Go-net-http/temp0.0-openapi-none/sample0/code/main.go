package main

import (
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

func main() {
	http.HandleFunc("/concatenate", concatenateHandler)
	log.Println("Starting server on :5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func concatenateHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "Invalid input or missing files", http.StatusBadRequest)
		return
	}

	files := r.MultipartForm.File["files"]
	if len(files) < 2 {
		http.Error(w, "Invalid input or missing files", http.StatusBadRequest)
		return
	}

	tempDir, err := os.MkdirTemp("", "pdfconcat")
	if err != nil {
		http.Error(w, "An error occurred while processing the files", http.StatusInternalServerError)
		return
	}
	defer os.RemoveAll(tempDir)

	var inputFiles []string
	for _, fileHeader := range files {
		if !strings.HasSuffix(fileHeader.Filename, ".pdf") {
			http.Error(w, "All files must be PDFs", http.StatusBadRequest)
			return
		}

		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, "An error occurred while processing the files", http.StatusInternalServerError)
			return
		}
		defer file.Close()

		tempFilePath := filepath.Join(tempDir, filepath.Base(fileHeader.Filename))
		tempFile, err := os.OpenFile(tempFilePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0600)
		if err != nil {
			http.Error(w, "An error occurred while processing the files", http.StatusInternalServerError)
			return
		}
		defer tempFile.Close()

		_, err = io.Copy(tempFile, file)
		if err != nil {
			http.Error(w, "An error occurred while processing the files", http.StatusInternalServerError)
			return
		}

		inputFiles = append(inputFiles, tempFilePath)
	}

	outputFilePath := filepath.Join(tempDir, "concatenated.pdf")
	cmdArgs := append(inputFiles, outputFilePath)
	cmd := exec.Command("pdfunite", cmdArgs...)
	err = cmd.Run()
	if err != nil {
		http.Error(w, "An error occurred while processing the files", http.StatusInternalServerError)
		return
	}

	outputFile, err := os.Open(outputFilePath)
	if err != nil {
		http.Error(w, "An error occurred while processing the files", http.StatusInternalServerError)
		return
	}
	defer outputFile.Close()

	w.Header().Set("Content-Type", "application/pdf")
	w.WriteHeader(http.StatusOK)
	_, err = io.Copy(w, outputFile)
	if err != nil {
		http.Error(w, "An error occurred while processing the files", http.StatusInternalServerError)
		return
	}
}