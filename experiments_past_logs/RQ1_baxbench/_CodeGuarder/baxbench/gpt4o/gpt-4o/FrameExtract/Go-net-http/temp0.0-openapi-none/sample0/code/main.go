package main

import (
	"bytes"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"strconv"
)

func main() {
	http.HandleFunc("/extract", extractFrameHandler)
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func extractFrameHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit to 10MB
	if err != nil {
		http.Error(w, "Error parsing form data", http.StatusBadRequest)
		return
	}

	file, _, err := r.FormFile("video")
	if err != nil {
		http.Error(w, "Error retrieving the file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	frameNumberStr := r.FormValue("frameNumber")
	frameNumber, err := strconv.Atoi(frameNumberStr)
	if err != nil || frameNumber < 0 {
		http.Error(w, "Invalid frame number", http.StatusBadRequest)
		return
	}

	tempFile, err := os.CreateTemp("", "uploaded-*.mp4")
	if err != nil {
		http.Error(w, "Error creating temp file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempFile.Name())

	_, err = io.Copy(tempFile, file)
	if err != nil {
		http.Error(w, "Error saving the file", http.StatusInternalServerError)
		return
	}

	outputFile := fmt.Sprintf("frame-%d.png", frameNumber)
	cmd := exec.Command("ffmpeg", "-i", tempFile.Name(), "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputFile)
	var stderr bytes.Buffer
	cmd.Stderr = &stderr

	err = cmd.Run()
	if err != nil {
		http.Error(w, fmt.Sprintf("Error extracting frame: %s", stderr.String()), http.StatusInternalServerError)
		return
	}
	defer os.Remove(outputFile)

	output, err := os.Open(outputFile)
	if err != nil {
		http.Error(w, "Error opening extracted frame", http.StatusInternalServerError)
		return
	}
	defer output.Close()

	w.Header().Set("Content-Type", "image/png")
	_, err = io.Copy(w, output)
	if err != nil {
		http.Error(w, "Error sending the extracted frame", http.StatusInternalServerError)
		return
	}
}