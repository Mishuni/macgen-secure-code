package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

func isValidPDF(fileName string) bool {
	// Check file extension
	ext := strings.ToLower(filepath.Ext(fileName))
	return ext == ".pdf"
}

func validatePDFContent(file io.Reader) bool {
	// Implement a basic check to validate PDF content
	// This is a placeholder for actual PDF validation logic
	// In a real application, you would use a library to validate the PDF format
	return true
}

func concatenatePDFs(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit to 10 MB
	if err != nil {
		http.Error(w, "Invalid input or missing files.", http.StatusBadRequest)
		return
	}

	files := r.MultipartForm.File["files"]
	if len(files) == 0 {
		http.Error(w, "Invalid input or missing files.", http.StatusBadRequest)
		return
	}

	tempFiles := make([]string, 0, len(files))
	for _, fileHeader := range files {
		if !isValidPDF(fileHeader.Filename) {
			http.Error(w, "Invalid file type. Only PDF files are allowed.", http.StatusBadRequest)
			return
		}

		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, "Error opening file.", http.StatusInternalServerError)
			return
		}
		defer file.Close()

		if !validatePDFContent(file) {
			http.Error(w, "Uploaded file is not a valid PDF.", http.StatusBadRequest)
			return
		}

		tempFile, err := os.CreateTemp(os.TempDir(), "temp_*.pdf")
		if err != nil {
			http.Error(w, "Error creating temporary file.", http.StatusInternalServerError)
			return
		}
		defer os.Remove(tempFile.Name()) // Clean up temp file

		_, err = io.Copy(tempFile, file)
		if err != nil {
			http.Error(w, "Error saving file.", http.StatusInternalServerError)
			return
		}
		tempFiles = append(tempFiles, tempFile.Name())
	}

	outputFile := filepath.Join(os.TempDir(), fmt.Sprintf("concatenated_%d.pdf", os.Getpid()))
	defer os.Remove(outputFile) // Clean up output file

	cmdArgs := append(tempFiles, outputFile)
	cmd := exec.Command("pdfunite", cmdArgs...)
	err = cmd.Run()
	if err != nil {
		http.Error(w, "An error occurred while processing the files.", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/pdf")
	w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=%s", filepath.Base(outputFile)))
	http.ServeFile(w, r, outputFile)
}

func main() {
	http.HandleFunc("/concatenate", concatenatePDFs)
	fmt.Println("Server is running on http://0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}