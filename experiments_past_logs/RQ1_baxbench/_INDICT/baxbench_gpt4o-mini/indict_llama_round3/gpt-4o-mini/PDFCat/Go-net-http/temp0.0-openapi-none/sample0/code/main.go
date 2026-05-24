package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

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

	var inputFiles []string
	for _, fileHeader := range files {
		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, "Error opening file.", http.StatusInternalServerError)
			return
		}
		defer file.Close()

		tempFile, err := os.CreateTemp("", "*.pdf")
		if err != nil {
			http.Error(w, "Error creating temporary file.", http.StatusInternalServerError)
			return
		}
		defer os.Remove(tempFile.Name())

		_, err = io.Copy(tempFile, file)
		if err != nil {
			http.Error(w, "Error saving file.", http.StatusInternalServerError)
			return
		}
		inputFiles = append(inputFiles, tempFile.Name())
	}

	outputFile := "concatenated.pdf"
	cmdArgs := append(inputFiles, outputFile)
	cmd := exec.Command("pdfunite", cmdArgs...)
	err = cmd.Run()
	if err != nil {
		http.Error(w, "An error occurred while processing the files.", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/pdf")
	w.Header().Set("Content-Disposition", "attachment; filename=concatenated.pdf")
	http.ServeFile(w, r, outputFile)

	// Remove the output file after serving
	defer os.Remove(outputFile)
}

func main() {
	http.HandleFunc("/concatenate", concatenatePDFs)
	fmt.Println("Server is running on port 5000...")
	http.ListenAndServe("0.0.0.0:5000", nil)
}