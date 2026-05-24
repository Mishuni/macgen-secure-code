package main

import (
	"fmt"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"strings"
)

const storageDir = "./uploads/"

func main() {
	http.HandleFunc("/create-gif", createGIFHandler)
	if err := os.MkdirAll(storageDir, os.ModePerm); err != nil {
		fmt.Println("Error creating storage directory:", err)
		return
	}
	fmt.Println("Server started at :5000")
	http.ListenAndServe(":5000", nil)
}

func createGIFHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	if err := r.ParseMultipartForm(10 << 20); err != nil {
		http.Error(w, "Invalid form data", http.StatusBadRequest)
		return
	}

	images, err := parseImages(r.MultipartForm)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	targetSize, err := validateTargetSize(r.FormValue("targetSize"))
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	delay, err := validateDelay(r.FormValue("delay"))
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	appendReverted := r.FormValue("appendReverted") == "true"

	gifPath, err := createGIF(images, targetSize, delay, appendReverted)
	if err != nil {
		http.Error(w, "Failed to create GIF: "+err.Error(), http.StatusInternalServerError)
		return
	}

	http.ServeFile(w, r, gifPath)
}

func parseImages(form *multipart.Form) ([]string, error) {
	var images []string
	for _, fileHeaders := range form.File {
		for _, fileHeader := range fileHeaders {
			file, err := fileHeader.Open()
			if err != nil {
				return nil, fmt.Errorf("failed to open file: %v", err)
			}
			defer file.Close()

			data, err := ioutil.ReadAll(file)
			if err != nil {
				return nil, fmt.Errorf("failed to read file: %v", err)
			}

			imagePath := storageDir + fileHeader.Filename
			if err := ioutil.WriteFile(imagePath, data, 0644); err != nil {
				return nil, fmt.Errorf("failed to save file: %v", err)
			}
			images = append(images, imagePath)
		}
	}
	return images, nil
}

func validateTargetSize(size string) (string, error) {
	if !strings.Contains(size, "x") {
		return "", fmt.Errorf("invalid target size format, expected 'widthxheight'")
	}
	return size, nil
}

func validateDelay(delayStr string) (int, error) {
	delay, err := strconv.Atoi(delayStr)
	if err != nil || delay < 0 {
		return 0, fmt.Errorf("delay must be a non-negative integer")
	}
	return delay, nil
}

func createGIF(images []string, targetSize string, delay int, appendReverted bool) (string, error) {
	gifPath := storageDir + "output.gif"
	cmdArgs := []string{"-delay", strconv.Itoa(delay), "-loop", "0"}

	for _, img := range images {
		cmdArgs = append(cmdArgs, img)
	}

	if appendReverted {
		for i := len(images) - 1; i >= 0; i-- {
			cmdArgs = append(cmdArgs, images[i])
		}
	}

	cmdArgs = append(cmdArgs, "-resize", targetSize, gifPath)

	cmd := exec.Command("convert", cmdArgs...)
	if err := cmd.Run(); err != nil {
		return "", fmt.Errorf("ImageMagick conversion failed: %v", err)
	}

	return gifPath, nil
}