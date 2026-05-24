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
)

func isValidVideoFile(fileName string) bool {
	allowedExtensions := []string{".mp4", ".avi", ".mov"}
	ext := strings.ToLower(filepath.Ext(fileName))
	for _, allowed := range allowedExtensions {
		if ext == allowed {
			return true
		}
	}
	return false
}

func extractFrameHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit upload size to 10 MB
	if err != nil {
		http.Error(w, "Unable to parse form", http.StatusBadRequest)
		return
	}

	videoFile, videoFileHeader, err := r.FormFile("video")
	if err != nil {
		http.Error(w, "Error retrieving video file", http.StatusBadRequest)
		return
	}
	defer videoFile.Close()

	if !isValidVideoFile(videoFileHeader.Filename) {
		http.Error(w, "Invalid video file type", http.StatusBadRequest)
		return
	}

	frameNumberStr := r.FormValue("frameNumber")
	frameNumber, err := strconv.Atoi(frameNumberStr)
	if err != nil || frameNumber < 0 {
		http.Error(w, "Invalid frame number", http.StatusBadRequest)
		return
	}

	// Create a temporary directory for video files
	tempDir, err := os.MkdirTemp("", "video-extract-")
	if err != nil {
		http.Error(w, "Unable to create temporary directory", http.StatusInternalServerError)
		return
	}
	defer os.RemoveAll(tempDir) // Clean up the temporary directory

	// Create a temporary file to save the uploaded video
	tempVideoFile, err := os.CreateTemp(tempDir, "video-*.mp4")
	if err != nil {
		http.Error(w, "Unable to create temporary video file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempVideoFile.Name())

	// Save the uploaded video to the temporary file
	_, err = io.Copy(tempVideoFile, videoFile)
	if err != nil {
		http.Error(w, "Error saving video file", http.StatusInternalServerError)
		return
	}

	// Generate the output image file name
	outputImageFile := filepath.Join(tempDir, fmt.Sprintf("frame-%d.png", frameNumber))

	// Use ffmpeg to extract the specified frame
	cmd := exec.Command("ffmpeg", "-i", tempVideoFile.Name(), "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImageFile)
	err = cmd.Run()
	if err != nil {
		http.Error(w, "Frame extraction failed", http.StatusInternalServerError)
		return
	}

	// Serve the extracted image
	w.Header().Set("Content-Type", "image/png")
	http.ServeFile(w, r, outputImageFile)
}

func main() {
	http.HandleFunc("/extract", extractFrameHandler)
	fmt.Println("Server is running on http://0.0.0.0:5000/extract")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}