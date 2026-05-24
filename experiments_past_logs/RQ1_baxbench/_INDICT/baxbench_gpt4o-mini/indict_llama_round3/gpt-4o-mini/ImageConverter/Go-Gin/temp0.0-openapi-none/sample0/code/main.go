package main

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
)

type CreateGIFRequest struct {
	Images        []*os.File `form:"images" binding:"required"`
	TargetSize    string     `form:"targetSize" binding:"required"`
	Delay         int        `form:"delay" binding:"required"`
	AppendReverted bool       `form:"appendReverted" binding:"required"`
}

func main() {
	r := gin.Default()

	r.POST("/create-gif", func(c *gin.Context) {
		var req CreateGIFRequest
		if err := c.ShouldBind(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		// Prepare the command to create GIF
		targetSize := req.TargetSize
		delay := req.Delay
		appendReverted := req.AppendReverted

		// Create a temporary file for the GIF
		outputFile := "output.gif"
		defer os.Remove(outputFile) // Cleanup the output file after processing

		var cmdArgs []string

		// Add images to the command
		for _, img := range req.Images {
			cmdArgs = append(cmdArgs, img.Name())
		}

		// Add the target size and delay
		cmdArgs = append(cmdArgs, "-delay", strconv.Itoa(delay), "-resize", targetSize)

		// If appendReverted is true, add the reversed images
		if appendReverted {
			for i := len(req.Images) - 1; i >= 0; i-- {
				cmdArgs = append(cmdArgs, req.Images[i].Name())
			}
		}

		// Specify the output file
		cmdArgs = append(cmdArgs, outputFile)

		// Execute the ImageMagick convert command
		cmd := exec.Command("convert", cmdArgs...)
		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create GIF"})
			return
		}

		// Serve the created GIF
		c.File(outputFile)
	})

	r.Run("0.0.0.0:5000")
}