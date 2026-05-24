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

func extractFrame(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseMultipartForm(10 << 20); err != nil {
		http.Error(w, "Unable to parse form", http.StatusBadRequest)
		return
	}

	videoFileName := r.FormValue("videoFileName")
	frameNumberStr := r.FormValue("frameNumber")
	videoFile, _, err := r.FormFile("video")
	if err != nil {
		http.Error(w, "Unable to get video file", http.StatusBadRequest)
		return
	}
	defer videoFile.Close()

	// Validate video file extension
	if !strings.HasSuffix(videoFileName, ".mp4") {
		http.Error(w, "Invalid video file type. Only .mp4 files are allowed.", http.StatusBadRequest)
		return
	}

	// Save the uploaded video file
	tempVideoFile, err := os.CreateTemp("", videoFileName)
	if err != nil {
		http.Error(w, "Unable to create temp video file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempVideoFile.Name())

	if _, err := io.Copy(tempVideoFile, videoFile); err != nil {
		http.Error(w, "Unable to save video file", http.StatusInternalServerError)
		return
	}

	frameNumber, err := strconv.Atoi(frameNumberStr)
	if err != nil || frameNumber < 0 {
		http.Error(w, "Invalid frame number", http.StatusBadRequest)
		return
	}

	// Get total number of frames
	cmd := exec.Command("ffmpeg", "-i", tempVideoFile.Name(), "-vf", "select=eq(n\\,0)", "-vframes", "1", "frame_check.png")
	if err := cmd.Run(); err != nil {
		http.Error(w, "Error checking video frames", http.StatusInternalServerError)
		return
	}
	defer os.Remove("frame_check.png")

	// Extract the frame using ffmpeg
	outputImage := fmt.Sprintf("frame_%d.png", frameNumber)
	cmd = exec.Command("ffmpeg", "-i", tempVideoFile.Name(), "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImage)
	if err := cmd.Run(); err != nil {
		http.Error(w, fmt.Sprintf("Frame at index %d could not be found.", frameNumber), http.StatusNotFound)
		return
	}
	defer os.Remove(outputImage)

	// Serve the extracted image
	w.Header().Set("Content-Type", "image/png")
	http.ServeFile(w, r, outputImage)
}

func main() {
	http.HandleFunc("/extract", extractFrame)
	fmt.Println("Server started at :5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}