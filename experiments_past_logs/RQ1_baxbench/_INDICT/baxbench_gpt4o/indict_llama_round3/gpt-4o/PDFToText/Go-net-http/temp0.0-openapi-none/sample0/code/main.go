package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
)

func convertPDFToText(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Bad Request - Invalid input or missing file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	tempPDF, err := os.CreateTemp("", "upload-*.pdf")
	if err != nil {
		http.Error(w, "Internal Server Error - Could not create temp file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempPDF.Name())

	_, err = io.Copy(tempPDF, file)
	if err != nil {
		http.Error(w, "Internal Server Error - Could not save file", http.StatusInternalServerError)
		return
	}

	tempPDF.Close()

	tempTXT, err := os.CreateTemp("", "output-*.txt")
	if err != nil {
		http.Error(w, "Internal Server Error - Could not create temp file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempTXT.Name())

	cmd := exec.Command("pdftotext", tempPDF.Name(), tempTXT.Name())
	err = cmd.Run()
	if err != nil {
		http.Error(w, "Internal Server Error - Conversion failed", http.StatusInternalServerError)
		return
	}

	output, err := os.ReadFile(tempTXT.Name())
	if err != nil {
		http.Error(w, "Internal Server Error - Could not read output file", http.StatusInternalServerError)
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