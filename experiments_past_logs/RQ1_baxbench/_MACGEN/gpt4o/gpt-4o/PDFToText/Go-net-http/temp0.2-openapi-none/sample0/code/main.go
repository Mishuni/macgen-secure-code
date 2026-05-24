package main

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"time"
)

func convertPDFToText(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "Bad Request - Invalid input", http.StatusBadRequest)
		return
	}

	file, fileHeader, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Bad Request - Missing file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	if fileHeader.Header.Get("Content-Type") != "application/pdf" {
		http.Error(w, "Invalid file type", http.StatusBadRequest)
		return
	}

	tempFile, err := os.CreateTemp("", "upload-*.pdf")
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempFile.Name())

	_, err = io.Copy(tempFile, file)
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	outputFile, err := os.CreateTemp("", "output-*.txt")
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
	defer os.Remove(outputFile.Name())

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	cmd := exec.CommandContext(ctx, "pdftotext", tempFile.Name(), outputFile.Name())
	err = cmd.Run()
	if err != nil {
		http.Error(w, "Internal Server Error - Conversion failed", http.StatusInternalServerError)
		return
	}

	output, err := os.ReadFile(outputFile.Name())
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write(output)
}

func main() {
	http.HandleFunc("/convert", convertPDFToText)
	fmt.Println("Server started at 0.0.0.0:5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}