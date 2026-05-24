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
	"time"
)

func main() {
	http.HandleFunc("/concatenate", concatenateHandler)
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func validFileName(name string) bool {
	for _, char := range name {
		if !(char >= 'a' && char <= 'z' || char >= 'A' && char <= 'Z' || char >= '0' && char <= '9' || char == '.' || char == '_') {
			return false
		}
	}
	return true
}

func concatenateHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "Invalid input or missing files.", http.StatusBadRequest)
		return
	}

	files := r.MultipartForm.File["files"]
	if len(files) == 0 {
		http.Error(w, "Invalid input or missing files.", http.StatusBadRequest)
		return
	}

	tempDir, err := os.MkdirTemp("", "pdfs")
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
	defer os.RemoveAll(tempDir)

	var inputFiles []string
	for _, fileHeader := range files {
		if strings.Contains(fileHeader.Filename, "..") || !validFileName(fileHeader.Filename) {
			http.Error(w, "Invalid file name.", http.StatusBadRequest)
			return
		}

		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
		defer file.Close()

		tempFilePath := filepath.Join(tempDir, fileHeader.Filename)
		tempFile, err := os.Create(tempFilePath)
		if err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
		defer tempFile.Close()

		_, err = io.Copy(tempFile, file)
		if err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}

		inputFiles = append(inputFiles, tempFilePath)
	}

	outputFilePath := filepath.Join(tempDir, "concatenated.pdf")
	cmdArgs := append(inputFiles, outputFilePath)
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	cmd := exec.CommandContext(ctx, "pdfunite", cmdArgs...)
	err = cmd.Run()
	if err != nil {
		http.Error(w, "An error occurred while processing the files.", http.StatusInternalServerError)
		return
	}

	outputFile, err := os.Open(outputFilePath)
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
	defer outputFile.Close()

	w.Header().Set("Content-Type", "application/pdf")
	w.WriteHeader(http.StatusOK)
	_, err = io.Copy(w, outputFile)
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
}