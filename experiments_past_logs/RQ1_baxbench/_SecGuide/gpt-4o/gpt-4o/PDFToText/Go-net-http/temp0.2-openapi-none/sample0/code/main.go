package main

import (
	"crypto/tls"
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

func convertPDFToText(w http.ResponseWriter, r *http.Request) {
	// Set response header to plain text
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")

	// Parse the multipart form
	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "Bad Request - Invalid input or missing file", http.StatusBadRequest)
		return
	}

	// Retrieve the file from form data
	file, handler, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Bad Request - Invalid input or missing file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Validate the file type
	if !isValidPDF(handler) {
		http.Error(w, "Bad Request - Uploaded file is not a valid PDF", http.StatusBadRequest)
		return
	}

	// Create a temporary file to store the uploaded PDF
	tempDir := os.TempDir()
	tempFile, err := os.CreateTemp(tempDir, "upload-*.pdf")
	if err != nil {
		http.Error(w, "Internal Server Error - Conversion failed", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempFile.Name())

	// Copy the uploaded file to the temporary file
	_, err = io.Copy(tempFile, file)
	if err != nil {
		http.Error(w, "Internal Server Error - Conversion failed", http.StatusInternalServerError)
		return
	}

	// Close the temporary file
	tempFile.Close()

	// Convert the PDF to text using pdftotext
	outputFile := tempFile.Name() + ".txt"
	cmd := exec.Command("pdftotext", tempFile.Name(), outputFile)
	err = cmd.Run()
	if err != nil {
		http.Error(w, "Internal Server Error - Conversion failed", http.StatusInternalServerError)
		return
	}
	defer os.Remove(outputFile)

	// Read the converted text file
	convertedText, err := os.ReadFile(outputFile)
	if err != nil {
		http.Error(w, "Internal Server Error - Conversion failed", http.StatusInternalServerError)
		return
	}

	// Write the converted text to the response
	w.Write(convertedText)
}

func isValidPDF(handler *multipart.FileHeader) bool {
	// Check the file extension
	ext := strings.ToLower(filepath.Ext(handler.Filename))
	if ext != ".pdf" {
		return false
	}

	// Check the file header for PDF magic number
	file, err := handler.Open()
	if err != nil {
		return false
	}
	defer file.Close()

	buffer := make([]byte, 4)
	_, err = file.Read(buffer)
	if err != nil {
		return false
	}

	return string(buffer) == "%PDF"
}

func cleanupOldTempFiles() {
	tempDir := os.TempDir()
	files, err := os.ReadDir(tempDir)
	if err != nil {
		log.Println("Error reading temp directory:", err)
		return
	}

	for _, file := range files {
		if strings.HasPrefix(file.Name(), "upload-") {
			filePath := filepath.Join(tempDir, file.Name())
			info, err := os.Stat(filePath)
			if err != nil {
				log.Println("Error stating file:", err)
				continue
			}

			// Remove files older than 1 hour
			if time.Since(info.ModTime()) > time.Hour {
				err := os.Remove(filePath)
				if err != nil {
					log.Println("Error removing file:", err)
				}
			}
		}
	}
}

func main() {
	go func() {
		for {
			cleanupOldTempFiles()
			time.Sleep(10 * time.Minute) // Adjusted frequency
		}
	}()

	http.HandleFunc("/convert", convertPDFToText)

	server := &http.Server{
		Addr: "0.0.0.0:5000",
		TLSConfig: &tls.Config{
			MinVersion: tls.VersionTLS12,
			// Add secure cipher suites
			CipherSuites: []uint16{
				tls.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
				tls.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
			},
		},
	}

	fmt.Println("Server started at 0.0.0.0:5000")
	log.Fatal(server.ListenAndServeTLS(os.Getenv("SERVER_CERT"), os.Getenv("SERVER_KEY")))
}