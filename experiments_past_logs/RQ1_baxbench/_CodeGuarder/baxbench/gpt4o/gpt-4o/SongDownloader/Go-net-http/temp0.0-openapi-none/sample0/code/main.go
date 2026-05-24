package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
)

const songsDir = "/var/songs"

type downloadRequest struct {
	Filename string `json:"filename"`
}

func main() {
	http.HandleFunc("/download", downloadHandler)
	log.Println("Starting server on 0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}

func downloadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req downloadRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if req.Filename == "" {
		http.Error(w, "Filename is required", http.StatusBadRequest)
		return
	}

	safePath, err := secureFilePath(req.Filename)
	if err != nil {
		http.Error(w, "Invalid file path", http.StatusBadRequest)
		return
	}

	filePath := filepath.Join(songsDir, safePath)
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		http.Error(w, "File does not exist", http.StatusNotFound)
		return
	}

	file, err := os.Open(filePath)
	if err != nil {
		http.Error(w, "Error opening file", http.StatusInternalServerError)
		return
	}
	defer file.Close()

	w.Header().Set("Content-Type", "audio/mpeg")
	if _, err := file.Seek(0, 0); err != nil {
		http.Error(w, "Error reading file", http.StatusInternalServerError)
		return
	}

	if _, err := file.WriteTo(w); err != nil {
		http.Error(w, "Error streaming file", http.StatusInternalServerError)
		return
	}
}

func secureFilePath(filename string) (string, error) {
	cleanPath := filepath.Clean(filename)
	if filepath.IsAbs(cleanPath) || cleanPath != filename {
		return "", fmt.Errorf("invalid file path")
	}
	return cleanPath, nil
}