package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/google/uuid"
)

const uploadDir = "/var/uploads"

func main() {
	http.HandleFunc("/upload", uploadHandler)
	http.HandleFunc("/images/", imageHandler)

	if err := os.MkdirAll(uploadDir, os.ModePerm); err != nil {
		fmt.Printf("Error creating upload directory: %v\n", err)
		return
	}

	fmt.Println("Server started at 0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Printf("Error starting server: %v\n", err)
	}
}

func uploadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	if err := r.ParseMultipartForm(10 << 20); err != nil {
		http.Error(w, "Invalid form data", http.StatusBadRequest)
		return
	}

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "File not found in request", http.StatusBadRequest)
		return
	}
	defer file.Close()

	fileHeader := make([]byte, 512)
	if _, err := file.Read(fileHeader); err != nil {
		http.Error(w, "Unable to read file", http.StatusInternalServerError)
		return
	}
	contentType := http.DetectContentType(fileHeader)
	if !strings.HasPrefix(contentType, "image/") {
		http.Error(w, "Invalid image file", http.StatusBadRequest)
		return
	}

	id := uuid.New().String()
	filePath := filepath.Join(uploadDir, id)

	out, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE, 0644)
	if err != nil {
		http.Error(w, "Unable to save the file", http.StatusInternalServerError)
		return
	}
	defer out.Close()

	file.Seek(0, 0)
	if _, err := io.Copy(out, file); err != nil {
		http.Error(w, "Failed to save the file", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"id":"%s"}`, id)
}

func imageHandler(w http.ResponseWriter, r *http.Request) {
	imageID := strings.TrimPrefix(r.URL.Path, "/images/")
	if imageID == "" {
		http.Error(w, "Image ID is required", http.StatusBadRequest)
		return
	}

	filePath := filepath.Join(uploadDir, filepath.Clean(imageID))
	if !strings.HasPrefix(filePath, uploadDir) {
		http.Error(w, "Invalid file path", http.StatusBadRequest)
		return
	}

	file, err := os.Open(filePath)
	if err != nil {
		http.Error(w, "Image not found", http.StatusNotFound)
		return
	}
	defer file.Close()

	fileHeader := make([]byte, 512)
	if _, err := file.Read(fileHeader); err != nil {
		http.Error(w, "Unable to read file", http.StatusInternalServerError)
		return
	}

	file.Seek(0, 0)
	contentType := http.DetectContentType(fileHeader)
	w.Header().Set("Content-Type", contentType)
	w.WriteHeader(http.StatusOK)
	if _, err := io.Copy(w, file); err != nil {
		http.Error(w, "Failed to send file", http.StatusInternalServerError)
	}
}