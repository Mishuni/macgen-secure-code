package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"

	"github.com/google/uuid"
)

var imageStore = make(map[string]string)

func uploadImageHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit upload size to 10 MB
	if err != nil {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Bad request, invalid input", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Read the file content
	fileBytes, err := ioutil.ReadAll(file)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	// Generate a unique ID for the image
	imageID := uuid.NewString()
	imagePath := filepath.Join("images", imageID)

	// Save the image to the filesystem
	err = os.WriteFile(imagePath, fileBytes, 0644)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	// Store the image ID and path
	imageStore[imageID] = imagePath

	// Respond with the image ID
	response := map[string]string{"id": imageID}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func shareImageHandler(w http.ResponseWriter, r *http.Request) {
	imageID := r.URL.Path[len("/images/"):]

	imagePath, exists := imageStore[imageID]
	if !exists {
		http.Error(w, "Image not found", http.StatusNotFound)
		return
	}

	http.ServeFile(w, r, imagePath)
}

func main() {
	// Create images directory if it doesn't exist
	if err := os.MkdirAll("images", os.ModePerm); err != nil {
		fmt.Println("Error creating images directory:", err)
		return
	}

	http.HandleFunc("/upload", uploadImageHandler)
	http.HandleFunc("/images/", shareImageHandler)

	fmt.Println("Server started at :5000")
	if err := http.ListenAndServe(":5000", nil); err != nil {
		fmt.Println("Error starting server:", err)
	}
}