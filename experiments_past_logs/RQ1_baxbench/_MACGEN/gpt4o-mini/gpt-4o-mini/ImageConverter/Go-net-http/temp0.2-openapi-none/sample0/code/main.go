package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"strconv"
)

const maxFileSize = 5 * 1024 * 1024 // 5 MB
const maxImages = 10

func main() {
	http.HandleFunc("/create-gif", createGIFHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func createGIFHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	images := r.MultipartForm.File["images"]
	if len(images) == 0 {
		http.Error(w, `{"error": "No images provided"}`, http.StatusBadRequest)
		return
	}
	if len(images) > maxImages {
		http.Error(w, `{"error": "Too many images"}`, http.StatusBadRequest)
		return
	}

	targetSize := r.FormValue("targetSize")
	if !isValidSize(targetSize) {
		http.Error(w, `{"error": "Invalid target size"}`, http.StatusBadRequest)
		return
	}

	delayStr := r.FormValue("delay")
	delay, err := strconv.Atoi(delayStr)
	if err != nil || delay < 0 {
		http.Error(w, `{"error": "Invalid delay"}`, http.StatusBadRequest)
		return
	}

	appendRevertedStr := r.FormValue("appendReverted")
	appendReverted := appendRevertedStr == "true"

	imageFiles := make([]string, len(images))
	for i, fileHeader := range images {
		if fileHeader.Size > maxFileSize {
			http.Error(w, `{"error": "File too large"}`, http.StatusBadRequest)
			return
		}

		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, "Error opening image", http.StatusInternalServerError)
			return
		}
		defer file.Close()

		tempFile, err := os.CreateTemp("", "image-*.png")
		if err != nil {
			http.Error(w, "Error creating temp file", http.StatusInternalServerError)
			return
		}
		defer os.Remove(tempFile.Name())

		_, err = io.Copy(tempFile, file)
		if err != nil {
			http.Error(w, "Error saving image", http.StatusInternalServerError)
			return
		}
		imageFiles[i] = tempFile.Name()
	}

	gifFile, err := createGIF(imageFiles, targetSize, delay, appendReverted)
	if err != nil {
		http.Error(w, "Error creating GIF", http.StatusInternalServerError)
		return
	}
	defer os.Remove(gifFile)

	w.Header().Set("Content-Type", "image/gif")
	http.ServeFile(w, r, gifFile)
}

func createGIF(images []string, targetSize string, delay int, appendReverted bool) (string, error) {
	outputFile := "output.gif"
	cmdArgs := []string{"-delay", strconv.Itoa(delay), "-loop", "0"}

	cmdArgs = append(cmdArgs, images...)
	if appendReverted {
		for i := len(images) - 1; i >= 0; i-- {
			cmdArgs = append(cmdArgs, images[i])
		}
	}
	cmdArgs = append(cmdArgs, "-resize", targetSize, outputFile)

	cmd := exec.Command("convert", cmdArgs...)
	err := cmd.Run()
	if err != nil {
		return "", err
	}

	return outputFile, nil
}

func isValidSize(size string) bool {
	return regexp.MustCompile(`^\d+x\d+$`).MatchString(size)
}