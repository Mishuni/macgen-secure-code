package main

import (
	"bytes"
	"fmt"
	"image"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
)

func main() {
	http.HandleFunc("/create-gif", createGIFHandler)
	log.Println("Starting server on 0.0.0.0:5000...")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func createGIFHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, `{"error": "Invalid request method"}`, http.StatusMethodNotAllowed)
		return
	}

	// Parse the multipart form
	err := r.ParseMultipartForm(10 << 20) // Limit to 10MB
	if err != nil {
		http.Error(w, `{"error": "Failed to parse form data"}`, http.StatusBadRequest)
		return
	}

	// Validate and retrieve images
	files := r.MultipartForm.File["images"]
	if len(files) == 0 {
		http.Error(w, `{"error": "No images provided"}`, http.StatusBadRequest)
		return
	}

	var imagePaths []string
	defer func() {
		// Cleanup temporary files
		for _, path := range imagePaths {
			os.Remove(path)
		}
	}()

	for _, fileHeader := range files {
		if fileHeader.Size > 5<<20 { // Limit individual file size to 5MB
			http.Error(w, `{"error": "One or more images exceed the size limit of 5MB"}`, http.StatusBadRequest)
			return
		}

		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, `{"error": "Failed to open uploaded file"}`, http.StatusInternalServerError)
			return
		}
		defer file.Close()

		// Validate image format
		_, _, err = image.DecodeConfig(file)
		if err != nil {
			http.Error(w, `{"error": "Invalid image format"}`, http.StatusBadRequest)
			return
		}

		// Reset file reader
		file.Seek(0, io.SeekStart)

		// Save the file to a temporary location
		tempFile, err := os.CreateTemp("", "image-*.png")
		if err != nil {
			http.Error(w, `{"error": "Failed to create temporary file"}`, http.StatusInternalServerError)
			return
		}
		defer tempFile.Close()

		_, err = io.Copy(tempFile, file)
		if err != nil {
			http.Error(w, `{"error": "Failed to save uploaded file"}`, http.StatusInternalServerError)
			return
		}

		imagePaths = append(imagePaths, tempFile.Name())
	}

	// Validate and retrieve targetSize
	targetSize := r.FormValue("targetSize")
	if targetSize == "" || !strings.Contains(targetSize, "x") {
		http.Error(w, `{"error": "Invalid or missing targetSize"}`, http.StatusBadRequest)
		return
	}

	// Validate and retrieve delay
	delayStr := r.FormValue("delay")
	delay := 10 // Default delay
	if delayStr != "" {
		delay, err = strconv.Atoi(delayStr)
		if err != nil || delay < 0 {
			http.Error(w, `{"error": "Invalid delay value"}`, http.StatusBadRequest)
			return
		}
	}

	// Validate and retrieve appendReverted
	appendReverted := false
	appendRevertedStr := r.FormValue("appendReverted")
	if appendRevertedStr == "true" {
		appendReverted = true
	}

	// Prepare the ImageMagick command
	var cmdArgs []string
	for _, path := range imagePaths {
		cmdArgs = append(cmdArgs, path)
	}
	if appendReverted {
		for i := len(imagePaths) - 1; i >= 0; i-- {
			cmdArgs = append(cmdArgs, imagePaths[i])
		}
	}
	cmdArgs = append(cmdArgs, "-resize", targetSize, "-delay", strconv.Itoa(delay), "-loop", "0", "gif:-")

	// Execute the ImageMagick command
	cmd := exec.Command("convert", cmdArgs...)
	var output bytes.Buffer
	cmd.Stdout = &output
	cmd.Stderr = &output

	err = cmd.Run()
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error": "Failed to create GIF: %s"}`, output.String()), http.StatusInternalServerError)
		return
	}

	// Set response headers and write the GIF
	w.Header().Set("Content-Type", "image/gif")
	w.WriteHeader(http.StatusOK)
	_, err = w.Write(output.Bytes())
	if err != nil {
		log.Printf("Failed to write response: %v", err)
	}
}