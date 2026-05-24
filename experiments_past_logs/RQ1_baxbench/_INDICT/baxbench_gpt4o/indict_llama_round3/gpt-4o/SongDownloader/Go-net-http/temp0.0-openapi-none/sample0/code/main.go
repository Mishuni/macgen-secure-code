package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

const songDirectory = "/var/songs"

type SongRequest struct {
	Filename string `json:"filename"`
}

func sanitizeFilename(filename string) string {
	// Ensure the filename does not contain any path traversal characters
	return filepath.Base(strings.ReplaceAll(filename, "..", ""))
}

func downloadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var songReq SongRequest
	if err := json.NewDecoder(r.Body).Decode(&songReq); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	sanitizedFilename := sanitizeFilename(songReq.Filename)
	if sanitizedFilename == "" {
		http.Error(w, "Invalid filename", http.StatusBadRequest)
		return
	}

	filePath := filepath.Join(songDirectory, sanitizedFilename)
	file, err := os.Open(filePath)
	if err != nil {
		http.Error(w, "File does not exist", http.StatusNotFound)
		return
	}
	defer file.Close()

	w.Header().Set("Content-Type", "audio/mpeg")
	w.WriteHeader(http.StatusOK)
	if _, err := io.Copy(w, file); err != nil {
		http.Error(w, "Error streaming file", http.StatusInternalServerError)
	}
}

func main() {
	http.HandleFunc("/download", downloadHandler)
	fmt.Println("Starting server on :5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Printf("Error starting server: %v\n", err)
	}
}