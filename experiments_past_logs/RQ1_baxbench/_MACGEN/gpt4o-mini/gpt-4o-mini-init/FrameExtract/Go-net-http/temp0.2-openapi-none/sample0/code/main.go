package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"strconv"
)

func isValidVideoType(mimeType string) bool {
	return mimeType == "video/mp4" || mimeType == "video/x-m4v"
}

func extractFrameHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "Unable to parse form", http.StatusBadRequest)
		return
	}

	videoFile, _, err := r.FormFile("video")
	if err != nil {
		http.Error(w, "Error retrieving video file", http.StatusBadRequest)
		return
	}
	defer videoFile.Close()

	// Validate video file type
	buff := make([]byte, 512)
	_, err = videoFile.Read(buff)
	if err != nil {
		http.Error(w, "Error reading video file", http.StatusInternalServerError)
		return
	}
	if !isValidVideoType(http.DetectContentType(buff)) {
		http.Error(w, "Invalid video file type", http.StatusBadRequest)
		return
	}

	// Reset the file pointer to the beginning
	videoFile.Seek(0, 0)

	frameNumberStr := r.FormValue("frameNumber")
	frameNumber, err := strconv.Atoi(frameNumberStr)
	if err != nil || frameNumber < 0 {
		http.Error(w, "Invalid frame number", http.StatusBadRequest)
		return
	}

	tempVideoFile, err := os.CreateTemp("", "video-*.mp4")
	if err != nil {
		http.Error(w, "Unable to create temp video file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempVideoFile.Name())

	_, err = io.Copy(tempVideoFile, videoFile)
	if err != nil {
		http.Error(w, "Error saving video file", http.StatusInternalServerError)
		return
	}

	outputImageFile := fmt.Sprintf("frame-%d.png", frameNumber)
	cmd := exec.Command("ffmpeg", "-i", tempVideoFile.Name(), "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImageFile)
	err = cmd.Run()
	if err != nil {
		http.Error(w, fmt.Sprintf("Frame at index %d could not be found.", frameNumber), http.StatusNotFound)
		return
	}
	defer os.Remove(outputImageFile)

	w.Header().Set("Content-Type", "image/png")
	http.ServeFile(w, r, outputImageFile)
}

func main() {
	http.HandleFunc("/extract", extractFrameHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}