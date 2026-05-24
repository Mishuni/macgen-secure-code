package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
)

const storageDir = "/var/songs"

type requestPayload struct {
	Filename string `json:"filename"`
}

func sanitizeAndValidatePath(filename string) (string, error) {
	// Ensure the filename is not empty
	if filename == "" {
		return "", fmt.Errorf("filename is empty")
	}

	// Resolve the absolute path of the requested file
	absPath := filepath.Join(storageDir, filename)
	absPath = filepath.Clean(absPath)

	// Ensure the resolved path is within the storage directory
	if !filepath.HasPrefix(absPath, storageDir) {
		return "", fmt.Errorf("invalid file path")
	}

	return absPath, nil
}

func downloadHandler(w http.ResponseWriter, r *http.Request) {
	// Ensure the request method is POST
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	// Ensure the content type is application/json
	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Invalid content type", http.StatusBadRequest)
		return
	}

	// Parse the JSON body
	var payload requestPayload
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&payload); err != nil {
		http.Error(w, "Invalid JSON payload", http.StatusBadRequest)
		return
	}

	// Sanitize and validate the filename
	filePath, err := sanitizeAndValidatePath(payload.Filename)
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	// Check if the file exists
	fileInfo, err := os.Stat(filePath)
	if os.IsNotExist(err) || fileInfo.IsDir() {
		http.Error(w, "File does not exist", http.StatusNotFound)
		return
	} else if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	// Open the file for reading
	file, err := os.Open(filePath)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer file.Close()

	// Set the appropriate headers for streaming the file
	w.Header().Set("Content-Type", "audio/mpeg")
	w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=%q", filepath.Base(filePath)))
	w.WriteHeader(http.StatusOK)

	// Stream the file content to the response
	if _, err := file.WriteTo(w); err != nil {
		http.Error(w, "Error streaming file", http.StatusInternalServerError)
		return
	}
}

func main() {
	http.HandleFunc("/download", downloadHandler)

	// Start the server on 0.0.0.0:5000
	fmt.Println("Starting server on 0.0.0.0:5000...")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Printf("Error starting server: %v\n", err)
	}
}