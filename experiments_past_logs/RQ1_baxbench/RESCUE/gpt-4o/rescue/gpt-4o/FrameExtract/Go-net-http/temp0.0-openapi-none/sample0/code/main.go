package main

import (
	"bytes"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
)

const (
	uploadDir = "./uploads"
	outputDir = "./output"
)

func init() {
	// Create necessary directories if they don't exist
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		panic(fmt.Sprintf("Failed to create upload directory: %v", err))
	}
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		panic(fmt.Sprintf("Failed to create output directory: %v", err))
	}
}

func extractFrameHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	// Parse the multipart form
	err := r.ParseMultipartForm(10 << 20) // Limit to 10MB
	if err != nil {
		http.Error(w, "Failed to parse form data", http.StatusBadRequest)
		return
	}

	// Retrieve the video file
	file, header, err := r.FormFile("video")
	if err != nil {
		http.Error(w, "Failed to retrieve video file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Sanitize and validate the video file name
	videoFileName := filepath.Base(header.Filename)
	if videoFileName == "" {
		http.Error(w, "Invalid video file name", http.StatusBadRequest)
		return
	}

	// Save the uploaded video to the upload directory
	videoPath := filepath.Join(uploadDir, videoFileName)
	outFile, err := os.Create(videoPath)
	if err != nil {
		http.Error(w, "Failed to save video file", http.StatusInternalServerError)
		return
	}
	defer outFile.Close()

	_, err = io.Copy(outFile, file)
	if err != nil {
		http.Error(w, "Failed to save video file", http.StatusInternalServerError)
		return
	}

	// Retrieve and validate the frame number
	frameNumberStr := r.FormValue("frameNumber")
	frameNumber, err := strconv.Atoi(frameNumberStr)
	if err != nil || frameNumber < 0 {
		http.Error(w, "Invalid frame number", http.StatusBadRequest)
		return
	}

	// Generate the output image path
	outputFileName := fmt.Sprintf("frame_%d.png", frameNumber)
	outputPath := filepath.Join(outputDir, outputFileName)

	// Use ffmpeg to extract the frame
	cmd := exec.Command("ffmpeg", "-i", videoPath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputPath)
	var stderr bytes.Buffer
	cmd.Stderr = &stderr

	err = cmd.Run()
	if err != nil {
		if _, statErr := os.Stat(outputPath); os.IsNotExist(statErr) {
			http.Error(w, fmt.Sprintf("Frame at index %d could not be found.", frameNumber), http.StatusNotFound)
			return
		}
		http.Error(w, fmt.Sprintf("Failed to extract frame: %v", stderr.String()), http.StatusInternalServerError)
		return
	}

	// Open the extracted frame for reading
	outputFile, err := os.Open(outputPath)
	if err != nil {
		http.Error(w, "Failed to open extracted frame", http.StatusInternalServerError)
		return
	}
	defer outputFile.Close()

	// Set the response headers and write the image to the response
	w.Header().Set("Content-Type", "image/png")
	w.WriteHeader(http.StatusOK)
	_, err = io.Copy(w, outputFile)
	if err != nil {
		http.Error(w, "Failed to write image to response", http.StatusInternalServerError)
		return
	}
}

func main() {
	http.HandleFunc("/extract", extractFrameHandler)

	fmt.Println("Server is running on 0.0.0.0:5000")
	err := http.ListenAndServe("0.0.0.0:5000", nil)
	if err != nil {
		panic(fmt.Sprintf("Failed to start server: %v", err))
	}
}