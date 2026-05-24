package main

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"strconv"

	"github.com/gin-gonic/gin"
)

type ExtractRequest struct {
	VideoFileName string `form:"videoFileName" binding:"required"`
	FrameNumber   int    `form:"frameNumber" binding:"required"`
	Video         *os.File `form:"video" binding:"required"`
}

func main() {
	router := gin.Default()
	router.POST("/extract", extractFrame)
	router.Run("0.0.0.0:5000")
}

func extractFrame(c *gin.Context) {
	var req ExtractRequest
	if err := c.ShouldBindMultipart(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	videoPath := fmt.Sprintf("/tmp/%s", req.VideoFileName)
	if err := c.SaveUploadedFile(req.Video, videoPath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save video file"})
		return
	}
	defer os.Remove(videoPath)

	outputImagePath := fmt.Sprintf("/tmp/frame_%d.png", req.FrameNumber)
	cmd := exec.Command("ffmpeg", "-i", videoPath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", req.FrameNumber), "-vsync", "vfr", outputImagePath)
	if err := cmd.Run(); err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": fmt.Sprintf("Frame at index %d could not be found.", req.FrameNumber)})
		return
	}
	defer os.Remove(outputImagePath)

	c.File(outputImagePath)
}