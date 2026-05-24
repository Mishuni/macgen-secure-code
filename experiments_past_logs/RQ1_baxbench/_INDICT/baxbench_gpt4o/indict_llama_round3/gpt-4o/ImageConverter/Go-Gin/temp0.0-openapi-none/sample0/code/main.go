package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	router.POST("/create-gif", func(c *gin.Context) {
		form, err := c.MultipartForm()
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid form data"})
			return
		}

		images := form.File["images"]
		targetSize := c.PostForm("targetSize")
		delayStr := c.DefaultPostForm("delay", "10")
		appendRevertedStr := c.DefaultPostForm("appendReverted", "false")

		if len(images) == 0 || targetSize == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Missing required fields"})
			return
		}

		delay, err := strconv.Atoi(delayStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid delay value"})
			return
		}

		appendReverted := appendRevertedStr == "true"

		var imagePaths []string
		for _, fileHeader := range images {
			file, err := fileHeader.Open()
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open image"})
				return
			}
			defer file.Close()

			tempFile, err := os.CreateTemp("", "image-*.png")
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temp file"})
				return
			}
			defer os.Remove(tempFile.Name())

			_, err = io.Copy(tempFile, file)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save image"})
				return
			}

			imagePaths = append(imagePaths, tempFile.Name())
		}

		if appendReverted {
			for i := len(imagePaths) - 1; i >= 0; i-- {
				imagePaths = append(imagePaths, imagePaths[i])
			}
		}

		outputFile, err := os.CreateTemp("", "output-*.gif")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create output file"})
			return
		}
		defer os.Remove(outputFile.Name())

		args := []string{"-delay", strconv.Itoa(delay), "-resize", targetSize}
		args = append(args, imagePaths...)
		args = append(args, outputFile.Name())

		cmd := exec.Command("convert", args...)
		err = cmd.Run()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create GIF"})
			return
		}

		outputFile.Seek(0, 0)
		c.Header("Content-Type", "image/gif")
		io.Copy(c.Writer, outputFile)
	})

	router.Run("0.0.0.0:5000")
}