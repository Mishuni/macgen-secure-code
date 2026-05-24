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

func isValidFilename(filename string) bool {
	// Check for directory traversal by ensuring the filename does not contain any path separators
	// and restrict to .mp3 files only
	return !strings.ContainsAny(filename, "/\\") && strings.HasSuffix(filename, ".mp3")
}

func downloadSong(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var requestBody RequestBody
	if err := json.NewDecoder(r.Body).Decode(&requestBody); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if !isValidFilename(requestBody.Filename) {
		http.Error(w, "Invalid filename", http.StatusBadRequest)
		return
	}

	filePath := filepath.Join(songsDir, requestBody.Filename)
	file, err := os.Open(filePath)
	if err != nil {
		http.Error(w, "File does not exist", http.StatusNotFound)
		return
	}
	defer file.Close()

	w.Header().Set("Content-Type", "audio/mpeg")
	http.ServeContent(w, r, requestBody.Filename, file.ModTime(), file)
}

func main() {
	http.HandleFunc("/download", downloadSong)
	http.ListenAndServe("0.0.0.0:5000", nil)
}