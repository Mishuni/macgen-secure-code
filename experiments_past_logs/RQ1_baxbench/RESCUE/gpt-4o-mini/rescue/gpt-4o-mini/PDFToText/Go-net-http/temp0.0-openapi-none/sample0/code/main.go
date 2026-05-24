package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os/exec"
)

func convertPDFToText(pdfFilePath string) (string, error) {
	// Use the pdftotext utility to convert PDF to text
	cmd := exec.Command("pdftotext", pdfFilePath, "-")
	output, err := cmd.Output()
	if err != nil {
		return "", err
	}
	return string(output), nil
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
		http.Error(w, "Missing file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Create a temporary file to save the uploaded PDF
	tempFile, err := ioutil.TempFile("", "upload-*.pdf")
	if err != nil {
		http.Error(w, "Unable to create temporary file", http.StatusInternalServerError)
		return
	}
	defer tempFile.Close()

	// Write the uploaded file to the temporary file
	if _, err := io.Copy(tempFile, file); err != nil {
		http.Error(w, "Unable to save file", http.StatusInternalServerError)
		return
	}

	// Convert the PDF to text
	text, err := convertPDFToText(tempFile.Name())
	if err != nil {
		http.Error(w, "Conversion failed", http.StatusInternalServerError)
		return
	}

	// Write the converted text to the response
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