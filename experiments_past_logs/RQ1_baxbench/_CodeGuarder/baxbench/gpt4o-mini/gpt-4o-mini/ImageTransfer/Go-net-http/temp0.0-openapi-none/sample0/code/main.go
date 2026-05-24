package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"

	"github.com/google/uuid"
)

type ImageMetadata struct {
	ID   string `json:"id"`
	Path string `json:"path"`
}

var imageStore = make(map[string]string)

func uploadImageHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit upload size to 10 MB
	if err != nil {
		http.Error(w, "Unable to parse form", http.StatusBadRequest)
		return
	}

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "No file uploaded", http.StatusBadRequest)
		return
	}
	defer file.Close()

	imageID := uuid.New().String()
	filePath := filepath.Join("uploads", imageID)

	out, err := os.Create(filePath)
	if err != nil {
		http.Error(w, "Unable to save file", http.StatusInternalServerError)
		return
	}
	defer out.Close()

	_, err = file.Seek(0, 0) // Reset file pointer
	if err != nil {
		http.Error(w, "Unable to read file", http.StatusInternalServerError)
		return
	}

	_, err = io.Copy(out, file)
	if err != nil {
		http.Error(w, "Unable to save file", http.StatusInternalServerError)
		return
	}

	imageStore[imageID] = filePath

	response := ImageMetadata{ID: imageID, Path: filePath}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func getImageHandler(w http.ResponseWriter, r *http.Request) {
	imageID := r.URL.Path[len("/images/"):]

	filePath, exists := imageStore[imageID]
	if !exists {
		http.Error(w, "Image not found", http.StatusNotFound)
		return
	}

	http.ServeFile(w, r, filePath)
}

func main() {
	if err := os.MkdirAll("uploads", os.ModePerm); err != nil {
		fmt.Println("Error creating uploads directory:", err)
		return
	}

	http.HandleFunc("/upload", uploadImageHandler)
	http.HandleFunc("/images/", getImageHandler)

	fmt.Println("Server is running on http://0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Error starting server:", err)
	}
}