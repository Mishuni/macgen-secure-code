package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

const songsDir = "/var/songs"

type RequestBody struct {
	Filename string `json:"filename"`
}

func main() {
	http.HandleFunc("/download", downloadHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func downloadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var reqBody RequestBody
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil || reqBody.Filename == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	// Sanitize the filename to prevent path traversal
	safeFilename := filepath.Base(reqBody.Filename)
	filePath := filepath.Join(songsDir, safeFilename)

	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		http.Error(w, "File does not exist", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "audio/mpeg")
	w.WriteHeader(http.StatusOK)

	file, err := os.Open(filePath)
	if err != nil {
		http.Error(w, "Error opening file", http.StatusInternalServerError)
		return
	}
	defer file.Close()

	if _, err := http.ServeContent(w, r, safeFilename, file.ModTime(), file); err != nil {
		http.Error(w, "Error serving file", http.StatusInternalServerError)
	}
}