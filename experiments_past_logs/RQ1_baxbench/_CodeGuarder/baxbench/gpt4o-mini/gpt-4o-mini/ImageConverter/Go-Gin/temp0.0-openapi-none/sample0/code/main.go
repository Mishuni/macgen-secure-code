package main

import (
	"fmt"
	"image"
	"image/gif"
	"image/jpeg"
	"image/png"
	"io"
	"math"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()
	router.POST("/create-gif", createGIFHandler)
	router.Run("0.0.0.0:5000")
}

func createGIFHandler(c *gin.Context) {
	// Parse multipart form data
	if err := c.Request.ParseMultipartForm(10 << 20); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid form data"})
		return
	}

	// Extract images
	formImages := c.Request.MultipartForm.File["images"]
	if len(formImages) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No images provided"})
		return
	}

	// Extract target size
	targetSizeStr := c.Request.FormValue("targetSize")
	targetSize := parseTargetSize(targetSizeStr)
	if targetSize == (0, 0) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid target size"})
		return
	}

	// Extract delay
	delayStr := c.Request.FormValue("delay")
	delay, err := strconv.Atoi(delayStr)
	if err != nil || delay <= 0 {
		delay = 10 // default delay
	}

	// Extract appendReverted flag
	appendRevertedStr := c.Request.FormValue("appendReverted")
	appendReverted := appendRevertedStr == "true"

	// Create GIF
	gifData, err := createGIF(formImages, targetSize, delay, appendReverted)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create GIF: " + err.Error()})
		return
	}

	// Return GIF
	c.Data(http.StatusOK, "image/gif", gifData)
}

func parseTargetSize(sizeStr string) (int, int) {
	parts := strings.Split(sizeStr, "x")
	if len(parts) != 2 {
		return 0, 0
	}
	width, err1 := strconv.Atoi(parts[0])
	height, err2 := strconv.Atoi(parts[1])
	if err1 != nil || err2 != nil || width <= 0 || height <= 0 {
		return 0, 0
	}
	return width, height
}

func createGIF(formImages []*http.FileHeader, targetSize (int, int), delay int, appendReverted bool) ([]byte, error) {
	var images []*image.Paletted
	for _, fileHeader := range formImages {
		file, err := fileHeader.Open()
		if err != nil {
			return nil, err
		}
		defer file.Close()

		img, _, err := image.Decode(file)
		if err != nil {
			return nil, err
		}

		resizedImg := resizeImage(img, targetSize)
		palettedImg := image.NewPaletted(resizedImg.Bounds(), nil)
		drawImageToPaletted(resizedImg, palettedImg)

		images = append(images, palettedImg)
	}

	if appendReverted {
		for i := len(images) - 1; i >= 0; i-- {
			images = append(images, images[i])
		}
	}

	var buf io.Writer
	gifData := new(gif.GIF)
	for _, img := range images {
		gifData.Image = append(gifData.Image, img)
		gifData.Delay = append(gifData.Delay, delay)
	}
	
	err := gif.EncodeAll(buf, gifData)
	if err != nil {
		return nil, err
	}

	return buf.(*bytes.Buffer).Bytes(), nil
}

func resizeImage(img image.Image, targetSize (int, int)) image.Image {
	// Resize logic here (omitted for brevity)
	return img
}

func drawImageToPaletted(src image.Image, dst *image.Paletted) {
	// Drawing logic here (omitted for brevity)
}