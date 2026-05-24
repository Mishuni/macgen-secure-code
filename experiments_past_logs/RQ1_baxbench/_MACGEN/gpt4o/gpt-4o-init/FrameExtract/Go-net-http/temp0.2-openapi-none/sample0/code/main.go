
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

func main() {
	http.HandleFunc("/extract", extractFrameHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func extractFrameHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "Unable to parse form", http.StatusBadRequest)
		return
	}

	file, handler, err := r.FormFile("video")
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

	// Validate file type
	buff := make([]byte, 512)
	_, err = file.Read(buff)
	if err != nil || http.DetectContentType(buff) != "video/mp4" {
		http.Error(w, "Invalid file type", http.StatusBadRequest)
		return
	}
	file.Seek(0, io.SeekStart)

	// Validate file name
	if strings.Contains(handler.Filename, "..") || filepath.Base(handler.Filename) != handler.Filename {
		http.Error(w, "Invalid file name", http.StatusBadRequest)
		return
	}

	tempVideoFile, err := os.CreateTemp("", "upload-*.mp4")
	if err != nil {
		http.Error(w, "Unable to create temp file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempVideoFile.Name())
	defer tempVideoFile.Close()

	_, err = io.Copy(tempVideoFile, file)
	if err != nil {
		http.Error(w, "Unable to save video file", http.StatusInternalServerError)
		return
	}

	outputImageFile := fmt.Sprintf("%s_frame_%d.png", tempVideoFile.Name(), frameNumber)
	cmd := exec.Command("ffmpeg", "-i", tempVideoFile.Name(), "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImageFile)
	err = cmd.Run()
	if err != nil {
		http.Error(w, "Error extracting frame", http.StatusInternalServerError)
		return
	}
	defer os.Remove(outputImageFile)

	outputFile, err := os.Open(outputImageFile)
	if err != nil {
		http.Error(w, "Frame not found at the specified index", http.StatusNotFound)
		return
	}
	defer outputFile.Close()

	w.Header().Set("Content-Type", "image/png")
	_, err = io.Copy(w, outputFile)
	if err != nil {
		http.Error(w, "Error sending the image", http.StatusInternalServerError)
		return
	}
}