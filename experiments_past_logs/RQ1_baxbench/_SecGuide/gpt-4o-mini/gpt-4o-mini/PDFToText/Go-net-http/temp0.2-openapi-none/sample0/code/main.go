package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"time"
)

func isValidPDFName(name string) bool {
	// Validate the filename to ensure it only contains allowed characters
	re := regexp.MustCompile(`^[a-zA-Z0-9._-]+\.pdf$`)
	return re.MatchString(name)
}

func isValidPDFContent(file io.Reader) (bool, error) {
	// Check the content type of the uploaded file
	buf := make([]byte, 512)
	if _, err := file.Read(buf); err != nil {
		return false, err
	}
	contentType := http.DetectContentType(buf)
	// Reset the file pointer for further reading
	if _, err := file.Seek(0, 0); err != nil {
		return false, err
	}
	return contentType == "application/pdf", nil
}

func convertPDFToText(pdfPath string) (string, error) {
	// Use pdftotext to convert PDF to text
	outputPath := pdfPath + ".txt"
	cmd := exec.Command("pdftotext", pdfPath, outputPath)
	cmd.Timeout = 10 * time.Second // Set a timeout for the command
	if err := cmd.Run(); err != nil {
		return "", err
	}

	// Read the converted text file
	text, err := os.ReadFile(outputPath)
	if err != nil {
		return "", err
	}

	// Clean up the output file
	os.Remove(outputPath)

	return string(text), nil
}

func convertHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	// Parse the multipart form
	err := r.ParseMultipartForm(10 << 20) // Limit to 10 MB
	if err != nil {
		http.Error(w, "Bad Request - Invalid input", http.StatusBadRequest)
		return
	}

	// Get the file from the form
	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Bad Request - Missing file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Validate the file type
	if !isValidPDFName(header.Filename) {
		http.Error(w, "Bad Request - Invalid file type", http.StatusBadRequest)
		return
	}

	// Validate the content type
	isValid, err := isValidPDFContent(file)
	if err != nil || !isValid {
		http.Error(w, "Bad Request - Invalid PDF content", http.StatusBadRequest)
		return
	}

	// Create a temporary file to save the uploaded PDF
	tempFile, err := os.CreateTemp("", "upload-*.pdf")
	if err != nil {
		http.Error(w, "Internal Server Error - Unable to create temp file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempFile.Name()) // Clean up the temp file

	// Copy the uploaded file to the temp file
	if _, err := io.Copy(tempFile, file); err != nil {
		http.Error(w, "Internal Server Error - Unable to save file", http.StatusInternalServerError)
		return
	}

	// Convert the PDF to text
	text, err := convertPDFToText(tempFile.Name())
	if err != nil {
		http.Error(w, "Internal Server Error - Conversion failed", http.StatusInternalServerError)
		return
	}

	// Set the content type and write the response
	w.Header().Set("Content-Type", "text/plain")
	w.Write([]byte(text))
}

func main() {
	http.HandleFunc("/convert", convertHandler)
	fmt.Println("Server is running on http://0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}