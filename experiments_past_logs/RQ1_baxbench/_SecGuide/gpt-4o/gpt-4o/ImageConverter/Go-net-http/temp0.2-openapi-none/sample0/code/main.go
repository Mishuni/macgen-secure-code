package main

import (
	"bytes"
	"crypto/tls"
	"fmt"
	"image"
	"image/gif"
	_ "image/jpeg"
	_ "image/png"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/nfnt/resize"
)

func main() {
	http.HandleFunc("/create-gif", createGifHandler)
	server := &http.Server{
		Addr: "0.0.0.0:5000",
		TLSConfig: &tls.Config{
			MinVersion: tls.VersionTLS12,
		},
	}
	log.Println("Starting server on 0.0.0.0:5000")
	log.Fatal(server.ListenAndServeTLS("server.crt", "server.key"))
}

func createGifHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB
	if err != nil {
		http.Error(w, "Invalid form data", http.StatusBadRequest)
		return
	}

	images := r.MultipartForm.File["images"]
	targetSize := r.FormValue("targetSize")
	delayStr := r.FormValue("delay")
	appendRevertedStr := r.FormValue("appendReverted")

	if len(images) == 0 || targetSize == "" {
		http.Error(w, "Missing required fields", http.StatusBadRequest)
		return
	}

	delay, err := strconv.Atoi(delayStr)
	if err != nil {
		delay = 10 // default delay
	}

	appendReverted := appendRevertedStr == "true"

	var frames []*image.Paletted
	var delays []int

	for _, fileHeader := range images {
		if !isValidImageType(fileHeader) {
			http.Error(w, "Invalid image type", http.StatusBadRequest)
			return
		}

		file, err := fileHeader.Open()
		if err != nil {
			http.Error(w, "Error reading image", http.StatusInternalServerError)
			return
		}

		img, _, err := image.Decode(file)
		file.Close() // Close the file immediately after decoding
		if err != nil {
			http.Error(w, "Error decoding image", http.StatusInternalServerError)
			return
		}

		width, height, err := parseTargetSize(targetSize)
		if err != nil {
			http.Error(w, "Invalid target size", http.StatusBadRequest)
			return
		}

		resizedImg := resize.Resize(uint(width), uint(height), img, resize.Lanczos3)
		palettedImg := image.NewPaletted(resizedImg.Bounds(), nil)
		quantizer := &gif.MedianCutQuantizer{}
		quantizer.Quantize(palettedImg, resizedImg.Bounds(), resizedImg, image.Point{})

		frames = append(frames, palettedImg)
		delays = append(delays, delay)
	}

	if appendReverted {
		for i := len(frames) - 1; i >= 0; i-- {
			frames = append(frames, frames[i])
			delays = append(delays, delay)
		}
	}

	var buf bytes.Buffer
	gif.EncodeAll(&buf, &gif.GIF{
		Image: frames,
		Delay: delays,
	})

	w.Header().Set("Content-Type", "image/gif")
	w.WriteHeader(http.StatusOK)
	io.Copy(w, &buf)
}

func parseTargetSize(targetSize string) (int, int, error) {
	parts := strings.Split(targetSize, "x")
	if len(parts) != 2 {
		return 0, 0, fmt.Errorf("invalid target size format")
	}

	width, err := strconv.Atoi(parts[0])
	if err != nil || width <= 0 {
		return 0, 0, fmt.Errorf("invalid width")
	}

	height, err := strconv.Atoi(parts[1])
	if err != nil || height <= 0 {
		return 0, 0, fmt.Errorf("invalid height")
	}

	return width, height, nil
}

func isValidImageType(fileHeader *multipart.FileHeader) bool {
	allowedTypes := []string{"image/jpeg", "image/png", "image/gif"}
	for _, t := range allowedTypes {
		if fileHeader.Header.Get("Content-Type") == t {
			return true
		}
	}
	return false
}