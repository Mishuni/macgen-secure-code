package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

var songsDir = "/var/songs" // Consider using environment variables for this in production

type RequestBody struct {
	Filename string `json:"filename"`
}

func downloadSong(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var reqBody RequestBody
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	// Validate filename to prevent directory traversal attacks
	if !isValidFilename(reqBody.Filename) {
		http.Error(w, "Invalid filename", http.StatusBadRequest)
		return
	}

	filePath := filepath.Join(songsDir, reqBody.Filename)

	// Check if the file exists and is within the allowed directory
	if !isFileInDirectory(filePath, songsDir) {
		http.Error(w, "File does not exist", http.StatusNotFound)
		return
	}

	file, err := os.Open(filePath)
	if err != nil {
		http.Error(w, "File does not exist", http.StatusNotFound)
		return
	}
	defer file.Close()

	// Validate file type
	if !isValidFileType(reqBody.Filename) {
		http.Error(w, "Invalid file type", http.StatusUnsupportedMediaType)
		return
	}

	w.Header().Set("Content-Type", "audio/mpeg")
	http.ServeContent(w, r, reqBody.Filename, file.ModTime(), file)
}

func isValidFilename(filename string) bool {
	// Enhanced validation to prevent directory traversal
	if strings.ContainsAny(filename, "../") || strings.Contains(filename, "\\") {
		return false
	}
	// Allow only alphanumeric characters, underscores, and dots
	for _, r := range filename {
		if !(r >= 'a' && r <= 'z' || r >= 'A' && r <= 'Z' || r >= '0' && r <= '9' || r == '_' || r == '.') {
			return false
		}
	}
	return true
}

func isFileInDirectory(filePath, dir string) bool {
	// Check if the file is within the specified directory
	absDir, _ := filepath.Abs(dir)
	absFilePath, _ := filepath.Abs(filePath)
	return strings.HasPrefix(absFilePath, absDir)
}

func isValidFileType(filename string) bool {
	// Check for valid audio file extensions
	allowedExtensions := []string{".mp3", ".wav", ".ogg"}
	for _, ext := range allowedExtensions {
		if strings.HasSuffix(filename, ext) {
			return true
		}
	}
	return false
}

func main() {
	http.HandleFunc("/download", downloadSong)
	http.ListenAndServe("0.0.0.0:5000", nil)
}