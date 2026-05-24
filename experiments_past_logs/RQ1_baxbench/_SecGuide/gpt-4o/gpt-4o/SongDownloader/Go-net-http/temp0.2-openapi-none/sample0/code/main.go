package main

import (
	"encoding/json"
	"fmt"
	"log"
	"mime"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

const songDirectory = "/var/songs"

type SongRequest struct {
	Filename string `json:"filename"`
}

func isValidFilename(filename string) bool {
	// Allow only alphanumeric characters, dots, dashes, and underscores
	for _, char := range filename {
		if !(char >= 'a' && char <= 'z' || char >= 'A' && char <= 'Z' || char >= '0' && char <= '9' || char == '.' || char == '-' || char == '_') {
			return false
		}
	}
	return true
}

func downloadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var songReq SongRequest
	decoder := json.NewDecoder(r.Body)
	err := decoder.Decode(&songReq)
	if err != nil || songReq.Filename == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	// Validate filename to prevent directory traversal attacks
	if !isValidFilename(songReq.Filename) {
		http.Error(w, "Invalid filename", http.StatusBadRequest)
		return
	}

	filePath := filepath.Join(songDirectory, songReq.Filename)
	file, err := os.Open(filePath)
	if err != nil {
		http.Error(w, "File does not exist", http.StatusNotFound)
		log.Printf("Error opening file: %v", err)
		return
	}
	defer file.Close()

	// Determine the content type based on the file extension
	ext := filepath.Ext(filePath)
	contentType := mime.TypeByExtension(ext)
	if contentType == "" {
		contentType = "application/octet-stream"
	}
	w.Header().Set("Content-Type", contentType)

	http.ServeContent(w, r, songReq.Filename, file.ModTime(), file)
}

func main() {
	http.HandleFunc("/download", downloadHandler)
	fmt.Println("Server starting on 0.0.0.0:5000")
	err := http.ListenAndServe("0.0.0.0:5000", nil)
	if err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}