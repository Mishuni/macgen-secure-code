package main

import (
	"fmt"
	"image/gif"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"os/exec"
	"strconv"
	"strings"
)

func main() {
	http.HandleFunc("/create-gif", createGIFHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func createGIFHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // Limit to 10 MB
	if err != nil {
		http.Error(w, "Failed to parse form: "+err.Error(), http.StatusBadRequest)
		return
	}

	files := r.MultipartForm.File["images"]
	if len(files) == 0 {
		http.Error(w, "No images provided", http.StatusBadRequest)
		return
	}

	targetSize := r.FormValue("targetSize")
	if targetSize == "" {
		http.Error(w, "Target size is required", http.StatusBadRequest)
		return
	}

	delayStr := r.FormValue("delay")
	delay := 10 // default delay
	if delayStr != "" {
		var err error
		delay, err = strconv.Atoi(delayStr)
		if err != nil || delay < 0 {
			http.Error(w, "Invalid delay value", http.StatusBadRequest)
			return
		}
	}

	appendRevertedStr := r.FormValue("appendReverted")
	appendReverted := false
	if appendRevertedStr != "" {
		appendReverted, err = strconv.ParseBool(appendRevertedStr)
		if err != nil {
			http.Error(w, "Invalid appendReverted value", http.StatusBadRequest)
			return
		}
	}

	imagePaths := make([]string, len(files))
	for i, fileHeader := range files {
		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, "Failed to open file: "+err.Error(), http.StatusInternalServerError)
			return
		}
		defer file.Close()

		tempFile, err := ioutil.TempFile("", "upload-*.png")
		if err != nil {
			http.Error(w, "Failed to create temp file: "+err.Error(), http.StatusInternalServerError)
			return
		}
		defer tempFile.Close()

		_, err = io.Copy(tempFile, file)
		if err != nil {
			http.Error(w, "Failed to save temp file: "+err.Error(), http.StatusInternalServerError)
			return
		}
		imagePaths[i] = tempFile.Name()
	}

	gifPath := "output.gif"
	defer os.Remove(gifPath)

	// Construct the ImageMagick command
	cmdArgs := []string{"convert"}
	cmdArgs = append(cmdArgs, imagePaths...)
	cmdArgs = append(cmdArgs, "-delay", strconv.Itoa(delay), "-loop", "0", gifPath)

	if appendReverted {
		cmdArgs = append(cmdArgs, "-reverse")
		cmdArgs = append(cmdArgs, imagePaths...)
	}

	cmd := exec.Command("magick", cmdArgs...)
	err = cmd.Run()
	if err != nil {
		http.Error(w, "Failed to create GIF: "+err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "image/gif")
	http.ServeFile(w, r, gifPath)
}