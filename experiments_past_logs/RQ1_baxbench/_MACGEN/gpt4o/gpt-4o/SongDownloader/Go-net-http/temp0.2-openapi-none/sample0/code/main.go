package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

const songDirectory = "/var/songs"

type requestPayload struct {
	Filename string `json:"filename"`
}

func downloadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	r.Body = http.MaxBytesReader(w, r.Body, 1048576) // Limit request body size to 1MB
	var payload requestPayload
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if payload.Filename == "" || strings.Contains(payload.Filename, "..") {
		http.Error(w, "Invalid filename", http.StatusBadRequest)
		return
	}

	filePath := filepath.Join(songDirectory, filepath.Clean(payload.Filename))
	file, err := os.Open(filePath)
	if err != nil {
		http.Error(w, "File does not exist", http.StatusNotFound)
		return
	}
	defer file.Close()

	w.Header().Set("Content-Type", "audio/mpeg")
	http.ServeContent(w, r, payload.Filename, file.ModTime(), file)
}

func main() {
	http.HandleFunc("/download", downloadHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}