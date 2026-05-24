package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/google/uuid"
)

const uploadDir = "./uploads"

type UploadResponse struct {
	ID string `json:"id"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

func main() {
	http.HandleFunc("/upload", uploadHandler)
	http.HandleFunc("/images/", imageHandler)

	if err := os.MkdirAll(uploadDir, os.ModePerm); err != nil {
		fmt.Println("Error creating upload directory:", err)
		return
	}

	fmt.Println("Server started at :5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func uploadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}
	defer file.Close()

	fileBytes, err := ioutil.ReadAll(file)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	fileType := http.DetectContentType(fileBytes)
	if !isValidImageType(fileType) {
		http.Error(w, "Invalid file type", http.StatusBadRequest)
		return
	}

	imageID := uuid.New().String()
	filePath := filepath.Join(uploadDir, imageID)

	if err := ioutil.WriteFile(filePath, fileBytes, 0644); err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	response := UploadResponse{ID: imageID}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func imageHandler(w http.ResponseWriter, r *http.Request) {
	imageID := strings.TrimPrefix(r.URL.Path, "/images/")
	if strings.Contains(imageID, "..") {
		http.Error(w, "Invalid image ID", http.StatusBadRequest)
		return
	}

	filePath := filepath.Join(uploadDir, imageID)

	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		http.Error(w, "Image not found", http.StatusNotFound)
		return
	}

	http.ServeFile(w, r, filePath)
}

func isValidImageType(fileType string) bool {
	return fileType == "image/jpeg" || fileType == "image/png" || fileType == "image/gif"
}