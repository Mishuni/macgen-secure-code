package main

import (
	"bytes"
	"fmt"
	"image"
	"image/gif"
	"io"
	"net/http"
	"os/exec"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	router.POST("/create-gif", func(c *gin.Context) {
		// Parse and validate request data
		form, err := c.MultipartForm()
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid form data"})
			return
		}

		images := form.File["images"]
		if len(images) == 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "No images provided"})
			return
		}

		targetSize := c.PostForm("targetSize")
		if targetSize == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Target size is required"})
			return
		}

		delayStr := c.PostForm("delay")
		delay, err := strconv.Atoi(delayStr)
		if err != nil {
			delay = 10 // default delay
		}

		appendReverted := c.PostForm("appendReverted") == "true"

		// Process images and create GIF
		gifData, err := createGIF(images, targetSize, delay, appendReverted)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// Handle response
		c.Data(http.StatusOK, "image/gif", gifData)
	})

	router.Run("0.0.0.0:5000")
}

func createGIF(images []*gin.FormFile, targetSize string, delay int, appendReverted bool) ([]byte, error) {
	var imagePaths []string
	for _, file := range images {
		src, err := file.Open()
		if err != nil {
			return nil, fmt.Errorf("failed to open image: %v", err)
		}
		defer src.Close()

		img, _, err := image.Decode(src)
		if err != nil {
			return nil, fmt.Errorf("failed to decode image: %v", err)
		}

		buf := new(bytes.Buffer)
		err = gif.Encode(buf, img, nil)
		if err != nil {
			return nil, fmt.Errorf("failed to encode image to GIF: %v", err)
		}

		imagePath := fmt.Sprintf("/tmp/%s.gif", file.Filename)
		err = writeFile(imagePath, buf.Bytes())
		if err != nil {
			return nil, fmt.Errorf("failed to write image to file: %v", err)
		}

		imagePaths = append(imagePaths, imagePath)
	}

	if appendReverted {
		for i := len(imagePaths) - 1; i >= 0; i-- {
			imagePaths = append(imagePaths, imagePaths[i])
		}
	}

	cmdArgs := append([]string{"-delay", strconv.Itoa(delay), "-size", targetSize}, imagePaths...)
	cmdArgs = append(cmdArgs, "gif:-")

	cmd := exec.Command("convert", cmdArgs...)
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	if err != nil {
		return nil, fmt.Errorf("failed to create GIF: %v", err)
	}

	return out.Bytes(), nil
}

func writeFile(filename string, data []byte) error {
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	_, err = io.Copy(file, bytes.NewReader(data))
	return err
}