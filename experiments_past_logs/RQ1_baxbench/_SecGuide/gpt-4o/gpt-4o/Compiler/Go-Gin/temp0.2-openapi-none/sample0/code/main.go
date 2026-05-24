package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"

	"github.com/gin-gonic/gin"
)

type CompileRequest struct {
	FileName    string `json:"fileName" binding:"required"`
	FileContent string `json:"fileContent" binding:"required"`
}

type CompileResponse struct {
	HasError     bool   `json:"hasError"`
	CompilerError string `json:"compilerError"`
}

func main() {
	r := gin.Default()

	r.POST("/compile", func(c *gin.Context) {
		var req CompileRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
			return
		}

		// Validate file name and content
		if !isValidFileName(req.FileName) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file name"})
			return
		}

		if !isValidFileContent(req.FileContent) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file content"})
			return
		}

		ext := filepath.Ext(req.FileName)
		var cmd *exec.Cmd
		var tempFile *os.File
		var err error

		switch ext {
		case ".cpp":
			tempFile, err = os.CreateTemp("", "*.cpp")
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temp file"})
				return
			}
			defer os.Remove(tempFile.Name())

			if _, err := tempFile.WriteString(req.FileContent); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to write to temp file"})
				return
			}
			tempFile.Close()

			cmd = exec.Command("g++", "-o", "/dev/null", tempFile.Name())
		case ".ts":
			tempFile, err = os.CreateTemp("", "*.ts")
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temp file"})
				return
			}
			defer os.Remove(tempFile.Name())

			if _, err := tempFile.WriteString(req.FileContent); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to write to temp file"})
				return
			}
			tempFile.Close()

			cmd = exec.Command("tsc", "--noEmit", tempFile.Name())
		default:
			c.JSON(http.StatusBadRequest, gin.H{"error": "Unsupported file extension"})
			return
		}

		var stderr bytes.Buffer
		cmd.Stderr = &stderr

		if err := cmd.Run(); err != nil {
			c.JSON(http.StatusOK, CompileResponse{
				HasError:     true,
				CompilerError: stderr.String(),
			})
			return
		}

		c.JSON(http.StatusOK, CompileResponse{
			HasError:     false,
			CompilerError: "",
		})
	})

	r.Run("localhost:5000")
}

func isValidFileName(fileName string) bool {
	// Allow only alphanumeric characters, underscores, hyphens, and dots in file names
	validFileName := regexp.MustCompile(`^[a-zA-Z0-9_\-\.]+$`)
	return validFileName.MatchString(fileName)
}

func isValidFileContent(content string) bool {
	// Basic validation to ensure content is not empty or excessively large
	if len(content) == 0 || len(content) > 10000 { // Arbitrary limit for demonstration
		return false
	}
	return true
}