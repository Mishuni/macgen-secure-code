package main

import (
	"bytes"
	"fmt"
	"image"
	"image/gif"
	"io"
	"log"
	"net/http"
	"os/exec"
	"strconv"
	"strings"
)

func main() {
	http.HandleFunc("/create-gif", createGifHandler)
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func createGifHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit upload size to 10MB
	if err != nil {
		http.Error(w, "Failed to parse form data", http.StatusBadRequest)
		return
	}

	images := r.MultipartForm.File["images"]
	if len(images) == 0 {
		http.Error(w, "No images uploaded", http.StatusBadRequest)
		return
	}

	targetSize := r.FormValue("targetSize")
	if targetSize == "" {
		http.Error(w, "Target size is required", http.StatusBadRequest)
		return
	}

	delayStr := r.FormValue("delay")
	delay, err := strconv.Atoi(delayStr)
	if err != nil || delay < 0 {
		http.Error(w, "Invalid delay value", http.StatusBadRequest)
		return
	}

	appendReverted := r.FormValue("appendReverted") == "true"

	var imagePaths []string
	for _, fileHeader := range images {
		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, "Failed to open image", http.StatusInternalServerError)
			return
		}
		defer file.Close()

		img, _, err := image.DecodeConfig(file)
		if err != nil {
			http.Error(w, "Invalid image format", http.StatusBadRequest)
			return
		}

		if img.Width <= 0 || img.Height <= 0 {
			http.Error(w, "Invalid image dimensions", http.StatusBadRequest)
			return
		}

		file.Seek(0, io.SeekStart)
		tempFile, err := createTempFile(file)
		if err != nil {
			http.Error(w, "Failed to save image", http.StatusInternalServerError)
			return
		}
		defer tempFile.Close()

		imagePaths = append(imagePaths, tempFile.Name())
	}

	if appendReverted {
		for i := len(imagePaths) - 1; i >= 0; i-- {
			imagePaths = append(imagePaths, imagePaths[i])
		}
	}

	output, err := createGif(imagePaths, targetSize, delay)
	if err != nil {
		http.Error(w, "Failed to create GIF", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "image/gif")
	w.Write(output)
}

func createTempFile(file io.Reader) (*os.File, error) {
	tempFile, err := os.CreateTemp("", "upload-*.png")
	if err != nil {
		return nil, err
	}

	_, err = io.Copy(tempFile, file)
	if err != nil {
		return nil, err
	}

	return tempFile, nil
}

func createGif(imagePaths []string, targetSize string, delay int) ([]byte, error) {
	args := append([]string{"-delay", strconv.Itoa(delay), "-resize", targetSize}, imagePaths...)
	args = append(args, "gif:-")

	cmd := exec.Command("convert", args...)
	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &out

	err := cmd.Run()
	if err != nil {
		return nil, fmt.Errorf("ImageMagick convert error: %v, output: %s", err, out.String())
	}

	return out.Bytes(), nil
}