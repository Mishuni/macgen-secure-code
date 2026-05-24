package main

import (
	"bytes"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

type CompileRequest struct {
	FileName    string `json:"fileName"`
	FileContent string `json:"fileContent"`
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
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		ext := filepath.Ext(req.FileName)
		var cmd *exec.Cmd
		var compilerError bytes.Buffer

		switch ext {
		case ".ts":
			tmpFile, err := os.CreateTemp("", "*.ts")
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temp file"})
				return
			}
			defer os.Remove(tmpFile.Name())

			if _, err := tmpFile.WriteString(req.FileContent); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to write to temp file"})
				return
			}
			tmpFile.Close()

			cmd = exec.Command("tsc", "--noEmit", tmpFile.Name())
		case ".cpp":
			tmpFile, err := os.CreateTemp("", "*.cpp")
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create temp file"})
				return
			}
			defer os.Remove(tmpFile.Name())

			if _, err := tmpFile.WriteString(req.FileContent); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to write to temp file"})
				return
			}
			tmpFile.Close()

			cmd = exec.Command("g++", "-o", "/dev/null", tmpFile.Name())
		default:
			c.JSON(http.StatusBadRequest, gin.H{"error": "Unsupported file extension"})
			return
		}

		cmd.Stderr = &compilerError
		err := cmd.Run()

		response := CompileResponse{
			HasError:     err != nil,
			CompilerError: strings.TrimSpace(compilerError.String()),
		}

		c.JSON(http.StatusOK, response)
	})

	r.Run("0.0.0.0:5000")
}