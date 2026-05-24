package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"os"
	"os/exec"
	"strings"

	"github.com/gin-gonic/gin"
)

type CompileRequest struct {
	FileName    string `json:"fileName" binding:"required"`
	FileContent string `json:"fileContent" binding:"required"`
}

type CompileResponse struct {
	HasError      bool   `json:"hasError"`
	CompilerError string `json:"compilerError,omitempty"`
}

func main() {
	r := gin.Default()

	r.POST("/compile", func(c *gin.Context) {
		var req CompileRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
			return
		}

		// Validate file extension
		if !strings.HasSuffix(req.FileName, ".ts") && !strings.HasSuffix(req.FileName, ".cpp") {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Unsupported file type. Only .ts and .cpp are allowed"})
			return
		}

		// Create a temporary file
		tempFile, err := os.CreateTemp("", req.FileName)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temporary file"})
			return
		}
		defer os.Remove(tempFile.Name()) // Ensure the file is deleted after use

		// Write the file content to the temporary file
		if _, err := tempFile.WriteString(req.FileContent); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to write to temporary file"})
			return
		}
		tempFile.Close()

		var cmd *exec.Cmd
		var stderr bytes.Buffer

		// Determine the compiler based on file extension
		if strings.HasSuffix(req.FileName, ".ts") {
			cmd = exec.Command("tsc", "--noEmit", tempFile.Name())
		} else if strings.HasSuffix(req.FileName, ".cpp") {
			cmd = exec.Command("g++", "-fsyntax-only", tempFile.Name())
		}

		// Capture standard error
		cmd.Stderr = &stderr

		// Run the compiler
		err = cmd.Run()

		// Prepare the response
		if err != nil {
			c.JSON(http.StatusOK, CompileResponse{
				HasError:      true,
				CompilerError: stderr.String(),
			})
		} else {
			c.JSON(http.StatusOK, CompileResponse{
				HasError:      false,
				CompilerError: "",
			})
		}
	})

	// Start the server
	r.Run("0.0.0.0:5000")
}