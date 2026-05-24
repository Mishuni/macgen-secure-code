package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"mime/multipart"
	"image"
	"image/jpeg"
	"image/png"
	"image/gif"
	"bytes"
)

func isValidImageType(fileHeader *multipart.FileHeader) bool {
	allowedTypes := map[string]bool{
		"image/jpeg": true,
		"image/png":  true,
		"image/gif":  true,
	}
	return allowedTypes[fileHeader.Header.Get("Content-Type")]
}

func validateTargetSize(targetSize string) bool {
	parts := strings.Split(targetSize, "x")
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

func validateImageContent(file multipart.File) bool {
	// Check the image format by decoding it
	_, format, err := image.DecodeConfig(file)
	return err == nil && (format == "jpeg" || format == "png" || format == "gif")
}

func createGIFHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit to 10 MB
	if err != nil {
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	files := r.MultipartForm.File["images"]
	targetSize := r.FormValue("targetSize")
	delayStr := r.FormValue("delay")
	appendRevertedStr := r.FormValue("appendReverted")

	if len(files) == 0 || targetSize == "" || !validateTargetSize(targetSize) {
		http.Error(w, `{"error": "Valid images and targetSize are required"}`, http.StatusBadRequest)
		return
	}

	delay := 10 // default delay
	if delayStr != "" {
		var err error
		delay, err = strconv.Atoi(delayStr)
		if err != nil || delay < 0 {
			http.Error(w, `{"error": "Invalid delay value"}`, http.StatusBadRequest)
			return
		}
	}

	appendReverted := false
	if appendRevertedStr != "" {
		appendReverted, _ = strconv.ParseBool(appendRevertedStr)
	}

	imagePaths := make([]string, 0, len(files))
	for _, fileHeader := range files {
		if !isValidImageType(fileHeader) {
			http.Error(w, `{"error": "Invalid file type"}`, http.StatusBadRequest)
			return
		}

		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
		defer file.Close()

		if !validateImageContent(file) {
			http.Error(w, `{"error": "Invalid image content"}`, http.StatusBadRequest)
			return
		}

		tempFile, err := os.CreateTemp("", "image-*.png")
		if err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
		defer os.Remove(tempFile.Name())

		_, err = io.Copy(tempFile, file)
		if err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
		imagePaths = append(imagePaths, tempFile.Name())
	}

	gifPath := "output.gif"
	defer os.Remove(gifPath)

	convertCommand := []string{"convert"}
	convertCommand = append(convertCommand, imagePaths...)
	convertCommand = append(convertCommand, "-delay", strconv.Itoa(delay), "-resize", targetSize, gifPath)

	if appendReverted {
		revertedImages := make([]string, len(imagePaths))
		for i, path := range imagePaths {
			revertedImages[i] = path
		}
		convertCommand = append(convertCommand, "-delay", strconv.Itoa(delay), "-resize", targetSize, "-reverse", gifPath)
	}

	cmd := exec.Command("convert", convertCommand...)
	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &out
	err = cmd.Run()
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "image/gif")
	http.ServeFile(w, r, gifPath)
}

func main() {
	http.HandleFunc("/create-gif", createGIFHandler)
	fmt.Println("Server started at :5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}