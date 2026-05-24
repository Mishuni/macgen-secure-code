package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"strings"
)

func createGIFHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, `{"error": "Method not allowed"}`, http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit to 10 MB
	if err != nil {
		http.Error(w, `{"error": "Bad Request"}`, http.StatusBadRequest)
		return
	}

	images := r.MultipartForm.File["images"]
	if len(images) == 0 {
		http.Error(w, `{"error": "No images provided"}`, http.StatusBadRequest)
		return
	}

	targetSize := r.FormValue("targetSize")
	if !isValidSize(targetSize) {
		http.Error(w, `{"error": "Invalid target size format"}`, http.StatusBadRequest)
		return
	}

	delayStr := r.FormValue("delay")
	delay := 10 // default delay
	if delayStr != "" {
		var err error
		delay, err = strconv.Atoi(delayStr)
		if err != nil {
			http.Error(w, `{"error": "Invalid delay value"}`, http.StatusBadRequest)
			return
		}
	}

	appendReverted := r.FormValue("appendReverted") == "true"

	imageFiles := make([]string, 0, len(images))
	for _, fileHeader := range images {
		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, `{"error": "Failed to open image"}`, http.StatusInternalServerError)
			return
		}
		defer file.Close()

		tempFile, err := os.CreateTemp("", "image-*.png")
		if err != nil {
			http.Error(w, `{"error": "Failed to create temp file"}`, http.StatusInternalServerError)
			return
		}

		if _, err = io.Copy(tempFile, file); err != nil {
			http.Error(w, `{"error": "Failed to save image"}`, http.StatusInternalServerError)
			return
		}
		imageFiles = append(imageFiles, tempFile.Name())
		tempFile.Close() // Close temp file after copying
	}

	gifFileName := "output.gif"
	defer os.Remove(gifFileName)

	cmdArgs := []string{"convert"}
	for _, img := range imageFiles {
		cmdArgs = append(cmdArgs, img)
	}
	if appendReverted {
		for i := len(imageFiles) - 1; i >= 0; i-- {
			cmdArgs = append(cmdArgs, imageFiles[i])
		}
	}
	cmdArgs = append(cmdArgs, "-delay", strconv.Itoa(delay), "-resize", targetSize, gifFileName)

	cmd := exec.Command("convert", cmdArgs[1:]...)
	if err := cmd.Run(); err != nil {
		http.Error(w, `{"error": "Failed to create GIF"}`, http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "image/gif")
	http.ServeFile(w, r, gifFileName)
}

func isValidSize(size string) bool {
	parts := strings.Split(size, "x")
	if len(parts) != 2 {
		return false
	}
	for _, part := range parts {
		if _, err := strconv.Atoi(part); err != nil {
			return false
		}
	}
	return true
}

func main() {
	http.HandleFunc("/create-gif", createGIFHandler)
	fmt.Println("Server is running on port 5000...")
	http.ListenAndServe("0.0.0.0:5000", nil)
}