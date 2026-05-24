package main

import (
	"crypto/tls"
	"fmt"
	"io"
	"log"
	"mime"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
)

func extractFrame(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	contentType := r.Header.Get("Content-Type")
	mediaType, _, err := mime.ParseMediaType(contentType)
	if err != nil || mediaType != "multipart/form-data" {
		http.Error(w, "Content-Type must be multipart/form-data", http.StatusBadRequest)
		return
	}

	err = r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "Unable to parse form", http.StatusBadRequest)
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

	tempVideoFile, err := os.CreateTemp("", "uploaded-*.mp4")
	if err != nil {
		http.Error(w, "Unable to create temp file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempVideoFile.Name())

	_, err = io.Copy(tempVideoFile, file)
	if err != nil {
		http.Error(w, "Unable to save file", http.StatusInternalServerError)
		return
	}

	tempVideoFile.Close()

	outputImageFile, err := os.CreateTemp("", "frame-*.png")
	if err != nil {
		http.Error(w, "Unable to create output file", http.StatusInternalServerError)
		return
	}
	outputImageFile.Close()
	defer os.Remove(outputImageFile.Name())

	cmd := exec.Command("ffmpeg", "-i", tempVideoFile.Name(), "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImageFile.Name())
	err = cmd.Run()
	if err != nil {
		http.Error(w, "Error extracting frame", http.StatusInternalServerError)
		return
	}

	outputFile, err := os.Open(outputImageFile.Name())
	if err != nil {
		http.Error(w, "Error opening extracted frame", http.StatusInternalServerError)
		return
	}
	defer outputFile.Close()

	w.Header().Set("Content-Type", "image/png")
	_, err = io.Copy(w, outputFile)
	if err != nil {
		http.Error(w, "Error sending extracted frame", http.StatusInternalServerError)
		return
	}
}

func main() {
	http.HandleFunc("/extract", extractFrame)
	server := &http.Server{
		Addr: "0.0.0.0:5000",
		TLSConfig: &tls.Config{
			MinVersion: tls.VersionTLS12,
		},
	}
	log.Println("Server started on :5000")
	log.Fatal(server.ListenAndServeTLS("server.crt", "server.key"))
}