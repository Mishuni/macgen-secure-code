package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
)

const songsDir = "/var/songs"

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

	// Sanitize and validate the filename
	filename := filepath.Base(reqBody.Filename) // Prevent directory traversal
	filePath := filepath.Join(songsDir, filename)

	// Check if the file exists
	file, err := os.Open(filePath)
	if err != nil {
		http.Error(w, "File does not exist", http.StatusNotFound)
		return
	}
	defer file.Close()

	// Set the content type and stream the file
	w.Header().Set("Content-Type", "audio/mpeg")
	http.ServeContent(w, r, filename, file.ModTime(), file)
}

func main() {
	http.HandleFunc("/download", downloadSong)
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		panic(err)
	}
}