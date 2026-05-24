package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"strconv"
)

const (
	maxImages      = 10
	maxImageSize   = 5 << 20 // 5 MB
	maxFormSize    = 50 << 20 // 50 MB
)

func main() {
	http.HandleFunc("/create-gif", createGifHandler)
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func createGifHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(maxFormSize)
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error": "Failed to parse form: %v"}`, err), http.StatusBadRequest)
		return
	}

	images := r.MultipartForm.File["images"]
	if len(images) == 0 || len(images) > maxImages {
		http.Error(w, `{"error": "Invalid number of images"}`, http.StatusBadRequest)
		return
	}

	targetSize := r.FormValue("targetSize")
	if !isValidTargetSize(targetSize) {
		http.Error(w, `{"error": "Invalid target size format"}`, http.StatusBadRequest)
		return
	}

	delayStr := r.FormValue("delay")
	delay, err := strconv.Atoi(delayStr)
	if err != nil || delay <= 0 {
		http.Error(w, `{"error": "Invalid delay value"}`, http.StatusBadRequest)
		return
	}

	appendReverted := r.FormValue("appendReverted") == "true"

	tempDir, err := os.MkdirTemp("", "gifcreator")
	if err != nil {
		http.Error(w, `{"error": "Failed to create temp directory"}`, http.StatusInternalServerError)
		return
	}
	defer os.RemoveAll(tempDir)

	var imagePaths []string
	for i, fileHeader := range images {
		if fileHeader.Size > maxImageSize {
			http.Error(w, `{"error": "Image file too large"}`, http.StatusBadRequest)
			return
		}

		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, `{"error": "Failed to open image file"}`, http.StatusInternalServerError)
			return
		}
		defer file.Close()

		imagePath := fmt.Sprintf("%s/image%d", tempDir, i)
		outFile, err := os.Create(imagePath)
		if err != nil {
			http.Error(w, `{"error": "Failed to create image file"}`, http.StatusInternalServerError)
			return
		}
		defer outFile.Close()

		_, err = io.Copy(outFile, file)
		if err != nil {
			http.Error(w, `{"error": "Failed to save image file"}`, http.StatusInternalServerError)
			return
		}

		imagePaths = append(imagePaths, imagePath)
	}

	if appendReverted {
		for i := len(imagePaths) - 1; i >= 0; i-- {
			imagePaths = append(imagePaths, imagePaths[i])
		}
	}

	outputGif := fmt.Sprintf("%s/output.gif", tempDir)
	args := append([]string{"-delay", strconv.Itoa(delay), "-resize", targetSize}, imagePaths...)
	args = append(args, outputGif)

	cmd := exec.Command("convert", args...)
	err = cmd.Run()
	if err != nil {
		http.Error(w, `{"error": "Failed to create GIF"}`, http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "image/gif")
	http.ServeFile(w, r, outputGif)
}

func isValidTargetSize(size string) bool {
	re := regexp.MustCompile(`^\d+x\d+$`)
	return re.MatchString(size)
}