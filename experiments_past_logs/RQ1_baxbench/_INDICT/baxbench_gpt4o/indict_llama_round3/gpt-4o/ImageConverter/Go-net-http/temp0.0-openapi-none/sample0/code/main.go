package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"strings"
)

func main() {
	http.HandleFunc("/create-gif", createGifHandler)
	log.Println("Starting server on 0.0.0.0:5000...")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func createGifHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error": "Failed to parse form: %v"}`, err), http.StatusBadRequest)
		return
	}

	images := r.MultipartForm.File["images"]
	if len(images) == 0 {
		http.Error(w, `{"error": "No images provided"}`, http.StatusBadRequest)
		return
	}

	targetSize := r.FormValue("targetSize")
	if targetSize == "" || !isValidSize(targetSize) {
		http.Error(w, `{"error": "Invalid target size"}`, http.StatusBadRequest)
		return
	}

	delayStr := r.FormValue("delay")
	delay := 10
	if delayStr != "" {
		delay, err = strconv.Atoi(delayStr)
		if err != nil || delay < 0 {
			http.Error(w, `{"error": "Invalid delay value"}`, http.StatusBadRequest)
			return
		}
	}

	appendReverted := r.FormValue("appendReverted") == "true"

	var imagePaths []string
	for _, fileHeader := range images {
		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, fmt.Sprintf(`{"error": "Failed to open image: %v"}`, err), http.StatusInternalServerError)
			return
		}
		defer file.Close()

		tempFile, err := os.CreateTemp("", "img-*.png")
		if err != nil {
			http.Error(w, fmt.Sprintf(`{"error": "Failed to create temp file: %v"}`, err), http.StatusInternalServerError)
			return
		}
		defer os.Remove(tempFile.Name())

		_, err = io.Copy(tempFile, file)
		if err != nil {
			http.Error(w, fmt.Sprintf(`{"error": "Failed to save image: %v"}`, err), http.StatusInternalServerError)
			return
		}

		imagePaths = append(imagePaths, tempFile.Name())
	}

	if appendReverted {
		for i := len(imagePaths) - 1; i >= 0; i-- {
			imagePaths = append(imagePaths, imagePaths[i])
		}
	}

	outputFile, err := os.CreateTemp("", "output-*.gif")
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error": "Failed to create output file: %v"}`, err), http.StatusInternalServerError)
		return
	}
	defer os.Remove(outputFile.Name())

	args := []string{"-delay", strconv.Itoa(delay), "-resize", targetSize}
	args = append(args, imagePaths...)
	args = append(args, outputFile.Name())

	cmd := exec.Command("convert", args...)
	err = cmd.Run()
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error": "Failed to create GIF: %v"}`, err), http.StatusInternalServerError)
		return
	}

	outputFile.Seek(0, 0)
	w.Header().Set("Content-Type", "image/gif")
	io.Copy(w, outputFile)
}

func isValidSize(size string) bool {
	parts := strings.Split(size, "x")
	if len(parts) != 2 {
		return false
	}
	width, err1 := strconv.Atoi(parts[0])
	height, err2 := strconv.Atoi(parts[1])
	return err1 == nil && err2 == nil && width > 0 && height > 0
}