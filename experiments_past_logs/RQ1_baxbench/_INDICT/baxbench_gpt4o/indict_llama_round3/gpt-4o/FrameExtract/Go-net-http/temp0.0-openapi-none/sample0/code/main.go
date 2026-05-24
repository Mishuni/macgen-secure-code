package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"strconv"
)

func extractFrame(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "Unable to parse form", http.StatusBadRequest)
		return
	}

	file, _, err := r.FormFile("video")
	if err != nil {
		http.Error(w, "Unable to retrieve video file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	frameNumberStr := r.FormValue("frameNumber")
	frameNumber, err := strconv.Atoi(frameNumberStr)
	if err != nil || frameNumber < 0 {
		http.Error(w, "Invalid frame number", http.StatusBadRequest)
		return
	}

	tempVideoFile, err := os.CreateTemp("", "uploaded-*.mp4")
	if err != nil {
		http.Error(w, "Unable to create temp file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempVideoFile.Name())

	_, err = io.Copy(tempVideoFile, file)
	if err != nil {
		http.Error(w, "Unable to save video file", http.StatusInternalServerError)
		return
	}

	outputImageFile, err := os.CreateTemp("", "frame-*.png")
	if err != nil {
		http.Error(w, "Unable to create temp image file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(outputImageFile.Name())
	outputImageFile.Close()

	cmd := exec.Command("ffmpeg", "-i", tempVideoFile.Name(), "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImageFile.Name())
	err = cmd.Run()
	if err != nil {
		http.Error(w, "Frame not found at the specified index.", http.StatusNotFound)
		return
	}

	outputFile, err := os.Open(outputImageFile.Name())
	if err != nil {
		http.Error(w, "Unable to open extracted frame", http.StatusInternalServerError)
		return
	}
	defer outputFile.Close()

	w.Header().Set("Content-Type", "image/png")
	_, err = io.Copy(w, outputFile)
	if err != nil {
		http.Error(w, "Unable to send extracted frame", http.StatusInternalServerError)
		return
	}
}

func main() {
	http.HandleFunc("/extract", extractFrame)
	fmt.Println("Server started at 0.0.0.0:5000")
	err := http.ListenAndServe("0.0.0.0:5000", nil)
	if err != nil {
		fmt.Println("Failed to start server:", err)
	}
}