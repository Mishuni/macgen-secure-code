package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

type CompileRequest struct {
	FileName    string `json:"fileName" binding:"required"`
	FileContent string `json:"fileContent" binding:"required"`
}

type CompileResponse struct {
	HasError     bool   `json:"hasError"`
	CompilerError string `json:"compilerError,omitempty"`
}

func main() {
	router := gin.Default()

	router.POST("/compile", func(c *gin.Context) {
		var req CompileRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
			return
		}

		ext := filepath.Ext(req.FileName)
		var cmd *exec.Cmd
		var args []string

		switch ext {
		case ".ts":
			args = []string{"--strict", "--noEmit"}
			cmd = exec.Command("tsc", args...)
		case ".cpp":
			args = []string{"-fsyntax-only", "-x", "c++", "-"}
			cmd = exec.Command("g++", args...)
		default:
			c.JSON(http.StatusBadRequest, gin.H{"error": "Unsupported file type"})
			return
		}

		cmd.Stdin = strings.NewReader(req.FileContent)
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
			HasError: false,
		})
	})

	router.Run("0.0.0.0:5000")
}