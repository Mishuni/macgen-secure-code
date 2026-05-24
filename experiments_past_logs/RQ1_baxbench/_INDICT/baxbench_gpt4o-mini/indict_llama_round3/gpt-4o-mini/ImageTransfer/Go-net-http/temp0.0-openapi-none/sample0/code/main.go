package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/google/uuid"
)

var imageStore = make(map[string]string)

func isValidImageType(fileName string) bool {
	ext := strings.ToLower(filepath.Ext(fileName))
	return ext == ".jpg" || ext == ".jpeg" || ext == ".png" || ext == ".gif" || ext == ".bmp" || ext == ".webp"
}

func uploadImageHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, `{"error": "Method not allowed"}`, http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit upload size to 10 MB
	if err != nil {
		http.Error(w, `{"error": "Bad request"}`, http.StatusBadRequest)
		return
	}

	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, `{"error": "Bad request"}`, http.StatusBadRequest)
		return
	}
	defer file.Close()

	if !isValidImageType(header.Filename) {
		http.Error(w, `{"error": "Invalid file type"}`, http.StatusBadRequest)
		return
	}

	id := uuid.New().String()
	filePath := filepath.Join("images", id)

	if err := os.MkdirAll("images", os.ModePerm); err != nil {
		http.Error(w, `{"error": "Internal server error"}`, http.StatusInternalServerError)
		return
	}

	out, err := os.Create(filePath)
	if err != nil {
		http.Error(w, `{"error": "Internal server error"}`, http.StatusInternalServerError)
		return
	}
	defer out.Close()

	if _, err = io.Copy(out, file); err != nil {
		http.Error(w, `{"error": "Internal server error"}`, http.StatusInternalServerError)
		return
	}

	imageStore[id] = filePath

	response := map[string]string{"id": id}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func shareImageHandler(w http.ResponseWriter, r *http.Request) {
	imageId := strings.TrimPrefix(r.URL.Path, "/images/")

	filePath, exists := imageStore[imageId]
	if !exists {
		http.Error(w, `{"error": "Image not found"}`, http.StatusNotFound)
		return
	}

	http.ServeFile(w, r, filePath)
}

func main() {
	http.HandleFunc("/upload", uploadImageHandler)
	http.HandleFunc("/images/", shareImageHandler)

	fmt.Println("Server started at :5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}