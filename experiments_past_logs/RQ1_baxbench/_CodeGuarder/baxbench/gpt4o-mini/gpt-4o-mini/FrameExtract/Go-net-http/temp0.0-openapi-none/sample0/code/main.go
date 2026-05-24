package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

type RequestBody struct {
	VideoFileName string `form:"videoFileName"`
	FrameNumber   int    `form:"frameNumber"`
	Video         io.Reader `form:"video"`
}

func extractFrameHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit to 10 MB
	if err != nil {
		http.Error(w, "Unable to parse form", http.StatusBadRequest)
		return
	}

	videoFileName := r.FormValue("videoFileName")
	frameNumber := r.FormValue("frameNumber")
	videoFile, _, err := r.FormFile("video")
	if err != nil {
		http.Error(w, "Error retrieving video file", http.StatusBadRequest)
		return
	}
	defer videoFile.Close()

	// Create a temporary file to save the uploaded video
	tempVideoFile, err := os.CreateTemp("", "*.mp4")
	if err != nil {
		http.Error(w, "Unable to create temporary video file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempVideoFile.Name()) // Clean up

	// Save the uploaded video to the temporary file
	if _, err := io.Copy(tempVideoFile, videoFile); err != nil {
		http.Error(w, "Error saving video file", http.StatusInternalServerError)
		return
	}

	// Construct the ffmpeg command to extract the frame
	outputImage := filepath.Join(os.TempDir(), fmt.Sprintf("frame_%d.png", frameNumber))
	cmd := exec.Command("ffmpeg", "-i", tempVideoFile.Name(), "-vf", fmt.Sprintf("select=eq(n\\,%s)", frameNumber), "-vframes", "1", outputImage)
	if err := cmd.Run(); err != nil {
		http.Error(w, "Error extracting frame", http.StatusInternalServerError)
		return
	}

	// Serve the extracted frame
	w.Header().Set("Content-Type", "image/png")
	http.ServeFile(w, r, outputImage)
}

func main() {
	http.HandleFunc("/extract", extractFrameHandler)
	fmt.Println("Server is running on port 5000...")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Error starting server:", err)
	}
}