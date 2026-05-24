package main

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

const maxUploadSize = 10 * 1024 * 1024 // 10 MB

type CreateGIFRequest struct {
	Images        []string `form:"images" binding:"required"`
	TargetSize    string   `form:"targetSize" binding:"required"`
	Delay         int      `form:"delay" binding:"default=10"`
	AppendReverted bool     `form:"appendReverted" binding:"default=false"`
}

func main() {
	router := gin.Default()
	router.POST("/create-gif", createGIFHandler)
	router.Run("0.0.0.0:5000")
}

func createGIFHandler(c *gin.Context) {
	if err := c.Request.ParseMultipartForm(maxUploadSize); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "File too large"})
		return
	}

	var req CreateGIFRequest
	if err := c.ShouldBind(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}

	if !isValidTargetSize(req.TargetSize) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid target size format"})
		return
	}

	if req.Delay < 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Delay must be a non-negative integer"})
		return
	}

	tempImageFiles := make([]string, len(req.Images))
	for i, image := range req.Images {
		file, err := c.FormFile(image)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve image"})
			return
		}

		tempFile, err := os.CreateTemp("", "image-*.png")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temporary file"})
			return
		}
		defer os.Remove(tempFile.Name())

		if err := c.SaveUploadedFile(file, tempFile.Name()); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save image"})
			return
		}
		tempImageFiles[i] = tempFile.Name()
	}

	outputGIF := "output.gif"
	cmdArgs := []string{"convert"}
	cmdArgs = append(cmdArgs, tempImageFiles...)
	if req.AppendReverted {
		cmdArgs = append(cmdArgs, "-reverse")
		cmdArgs = append(cmdArgs, tempImageFiles...)
	}
	cmdArgs = append(cmdArgs, "-delay", strconv.Itoa(req.Delay), "-resize", req.TargetSize, outputGIF)

	cmd := exec.Command("convert", cmdArgs...)
	if err := cmd.Run(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create GIF"})
		return
	}

	c.File(outputGIF)
	defer os.Remove(outputGIF)
}

func isValidTargetSize(size string) bool {
	re := regexp.MustCompile(`^\d+x\d+$`)
	return re.MatchString(size)
}