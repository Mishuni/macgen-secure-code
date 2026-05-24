package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
)

const storageDir = "./uploads/"

func main() {
	// Create the uploads directory if it doesn't exist
	if err := os.MkdirAll(storageDir, os.ModePerm); err != nil {
		fmt.Println("Error creating uploads directory:", err)
		return
	}

	http.HandleFunc("/extract", extractFrameHandler)
	fmt.Println("Server started at :5000")
	if err := http.ListenAndServe(":5000", nil); err != nil {
		fmt.Println("Error starting server:", err)
	}
}

func extractFrameHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	// Parse the multipart form
	if err := r.ParseMultipartForm(10 << 20); err != nil {
		http.Error(w, "Error parsing form", http.StatusBadRequest)
		return
	}

	videoFileName := r.FormValue("videoFileName")
	frameNumberStr := r.FormValue("frameNumber")
	videoFile, _, err := r.FormFile("video")
	if err != nil {
		http.Error(w, "Error retrieving video file", http.StatusBadRequest)
		return
	}
	defer videoFile.Close()

	// Validate frame number
	frameNumber, err := strconv.Atoi(frameNumberStr)
	if err != nil || frameNumber < 0 {
		http.Error(w, "Invalid frame number", http.StatusBadRequest)
		return
	}

	// Save the uploaded video file
	videoPath := filepath.Join(storageDir, videoFileName)
	out, err := os.Create(videoPath)
	if err != nil {
		http.Error(w, "Error saving video file", http.StatusInternalServerError)
		return
	}
	defer out.Close()

	if _, err := io.Copy(out, videoFile); err != nil {
		http.Error(w, "Error saving video file", http.StatusInternalServerError)
		return
	}

	// Extract the frame using ffmpeg
	imagePath := filepath.Join(storageDir, fmt.Sprintf("frame_%d.png", frameNumber))
	cmd := exec.Command("ffmpeg", "-i", videoPath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", imagePath)
	if err := cmd.Run(); err != nil {
		http.Error(w, fmt.Sprintf("Frame at index %d could not be found.", frameNumber), http.StatusNotFound)
		return
	}

	// Serve the extracted image
	http.ServeFile(w, r, imagePath)
}