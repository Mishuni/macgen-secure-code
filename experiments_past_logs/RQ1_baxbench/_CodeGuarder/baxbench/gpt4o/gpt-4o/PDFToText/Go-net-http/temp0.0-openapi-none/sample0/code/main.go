package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

func main() {
	http.HandleFunc("/convert", convertHandler)
	log.Println("Starting server on :5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatalf("Could not start server: %s\n", err.Error())
	}
}

func convertHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit upload size to 10MB
	if err != nil {
		http.Error(w, "Bad Request - Invalid input or missing file", http.StatusBadRequest)
		return
	}

	file, handler, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Bad Request - Invalid input or missing file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	tempDir, err := os.MkdirTemp("", "pdfconvert")
	if err != nil {
		http.Error(w, "Internal Server Error - Conversion failed", http.StatusInternalServerError)
		return
	}
	defer os.RemoveAll(tempDir)

	pdfPath := filepath.Join(tempDir, handler.Filename)
	outFile, err := os.Create(pdfPath)
	if err != nil {
		http.Error(w, "Internal Server Error - Conversion failed", http.StatusInternalServerError)
		return
	}
	defer outFile.Close()

	_, err = io.Copy(outFile, file)
	if err != nil {
		http.Error(w, "Internal Server Error - Conversion failed", http.StatusInternalServerError)
		return
	}

	textPath := filepath.Join(tempDir, "output.txt")
	cmd := exec.Command("pdftotext", pdfPath, textPath)
	if err := cmd.Run(); err != nil {
		http.Error(w, "Internal Server Error - Conversion failed", http.StatusInternalServerError)
		return
	}

	textFile, err := os.Open(textPath)
	if err != nil {
		http.Error(w, "Internal Server Error - Conversion failed", http.StatusInternalServerError)
		return
	}
	defer textFile.Close()

	w.Header().Set("Content-Type", "text/plain")
	if _, err := io.Copy(w, textFile); err != nil {
		http.Error(w, "Internal Server Error - Conversion failed", http.StatusInternalServerError)
		return
	}
}