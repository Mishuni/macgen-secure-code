package main

import (
	"bytes"
	"fmt"
	"image"
	_ "image/jpeg"
	_ "image/png"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"

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

		// Validate targetSize
		sizePattern := regexp.MustCompile(`^\d+x\d+$`)
		if !sizePattern.MatchString(targetSize) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid target size format"})
			return
		}

		delay, err := strconv.Atoi(delayStr)
		if err != nil || delay < 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid delay value"})
			return
		}

		appendReverted := appendRevertedStr == "true"

		tempDir, err := os.MkdirTemp("", "gifcreator")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temporary directory"})
			return
		}
		defer os.RemoveAll(tempDir)

		var imagePaths []string
		for _, fileHeader := range images {
			file, err := fileHeader.Open()
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open image file"})
				return
			}
			defer file.Close()

			// Validate image type
			_, format, err := image.DecodeConfig(file)
			if err != nil || (format != "jpeg" && format != "png") {
				c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid image format"})
				return
			}

			// Reset file pointer
			file.Seek(0, io.SeekStart)

			// Sanitize filename
			safeFileName := filepath.Base(fileHeader.Filename)
			tempFilePath := filepath.Join(tempDir, safeFileName)

			outFile, err := os.Create(tempFilePath)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temporary image file"})
				return
			}
			defer outFile.Close()

			_, err = io.Copy(outFile, file)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save image file"})
				return
			}

			imagePaths = append(imagePaths, tempFilePath)
		}

		if appendReverted {
			for i := len(imagePaths) - 1; i >= 0; i-- {
				imagePaths = append(imagePaths, imagePaths[i])
			}
		}

		gifPath := filepath.Join(tempDir, "output.gif")
		cmdArgs := append([]string{"-delay", strconv.Itoa(delay), "-resize", targetSize}, imagePaths...)
		cmdArgs = append(cmdArgs, gifPath)

		cmd := exec.Command("convert", cmdArgs...)
		var stderr bytes.Buffer
		cmd.Stderr = &stderr

		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("Failed to create GIF: %s", stderr.String())})
			return
		}

		c.Header("Content-Type", "image/gif")
		c.Header("Content-Disposition", "attachment; filename=output.gif")
		c.Header("X-Content-Type-Options", "nosniff")
		c.File(gifPath)
	})

	router.Run("0.0.0.0:5000")
}