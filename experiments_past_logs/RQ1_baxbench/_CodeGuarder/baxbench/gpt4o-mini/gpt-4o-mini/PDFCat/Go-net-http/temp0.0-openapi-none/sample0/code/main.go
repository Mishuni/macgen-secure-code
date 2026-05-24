package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

func main() {
	http.HandleFunc("/concatenate", concatenateHandler)
	fmt.Println("Server is listening on port 5000...")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Printf("Failed to start server: %v\n", err)
	}
}

func concatenateHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit to 10 MB
	if err != nil {
		http.Error(w, "Failed to parse form", http.StatusBadRequest)
		return
	}

	files := r.MultipartForm.File["files"]
	if len(files) == 0 {
		http.Error(w, "Invalid input or missing files", http.StatusBadRequest)
		return
	}

	tempDir, err := ioutil.TempDir("", "pdfconcat")
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
	defer os.RemoveAll(tempDir)

	var inputFiles []string
	for _, fileHeader := range files {
		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
		defer file.Close()

		tempFilePath := filepath.Join(tempDir, fileHeader.Filename)
		outFile, err := os.Create(tempFilePath)
		if err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
		defer outFile.Close()

		if _, err := io.Copy(outFile, file); err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
		inputFiles = append(inputFiles, tempFilePath)
	}

	outputFilePath := filepath.Join(tempDir, "concatenated.pdf")
	cmd := exec.Command("pdfunite", inputFiles...)
	cmd.Args = append(cmd.Args, outputFilePath)
	if err := cmd.Run(); err != nil {
		http.Error(w, "An error occurred while processing the files", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/pdf")
	http.ServeFile(w, r, outputFilePath)
}