package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

const maxFileSize = 10 * 1024 * 1024 // 10 MB

func concatenatePDFsHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(maxFileSize)
	if err != nil {
		http.Error(w, "Invalid input or missing files.", http.StatusBadRequest)
		return
	}

	files := r.MultipartForm.File["files"]
	if len(files) == 0 {
		http.Error(w, "Invalid input or missing files.", http.StatusBadRequest)
		return
	}

	var inputFiles []string
	for _, fileHeader := range files {
		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, "An error occurred while processing the files.", http.StatusInternalServerError)
			return
		}
		defer file.Close()

		buff := make([]byte, 512)
		_, err = file.Read(buff)
		if err != nil {
			http.Error(w, "An error occurred while processing the files.", http.StatusInternalServerError)
			return
		}
		file.Seek(0, 0) // Reset file pointer

		if http.DetectContentType(buff) != "application/pdf" {
			http.Error(w, "Invalid file type", http.StatusBadRequest)
			return
		}

		tempFile, err := os.CreateTemp("", "*.pdf")
		if err != nil {
			http.Error(w, "An error occurred while processing the files.", http.StatusInternalServerError)
			return
		}
		defer os.Remove(tempFile.Name())

		if _, err := io.Copy(tempFile, file); err != nil {
			http.Error(w, "An error occurred while processing the files.", http.StatusInternalServerError)
			return
		}
		inputFiles = append(inputFiles, tempFile.Name())
	}

	outputFile, err := os.CreateTemp("", "concatenated-*.pdf")
	if err != nil {
		http.Error(w, "An error occurred while processing the files.", http.StatusInternalServerError)
		return
	}
	defer os.Remove(outputFile.Name())

	cmdArgs := append(inputFiles, outputFile.Name())
	cmd := exec.Command("pdfunite", cmdArgs...)
	if err := cmd.Run(); err != nil {
		http.Error(w, "An error occurred while processing the files.", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/pdf")
	w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=%s", filepath.Base(outputFile.Name())))
	http.ServeFile(w, r, outputFile.Name())
}

func main() {
	http.HandleFunc("/concatenate", concatenatePDFsHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}