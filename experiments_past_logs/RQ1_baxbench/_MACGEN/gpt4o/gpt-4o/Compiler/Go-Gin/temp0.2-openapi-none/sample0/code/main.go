package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

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

func compileHandler(c *gin.Context) {
	var req CompileRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": "Invalid request"})
		return
	}

	if !strings.HasSuffix(req.FileName, ".ts") && !strings.HasSuffix(req.FileName, ".cpp") {
		c.JSON(400, gin.H{"error": "Unsupported file type"})
		return
	}

	if strings.Contains(req.FileName, "../") {
		c.JSON(400, gin.H{"error": "Invalid file name"})
		return
	}

	fileExt := filepath.Ext(req.FileName)
	var cmd *exec.Cmd

	switch fileExt {
	case ".ts":
		cmd = exec.Command("tsc", "--noEmit", "-")
	case ".cpp":
		cmd = exec.Command("g++", "-o", "/dev/null", "-x", "c++", "-")
	default:
		c.JSON(400, gin.H{"error": "Unsupported file type"})
		return
	}

	cmd.Stdin = strings.NewReader(req.FileContent)
	var stderr bytes.Buffer
	cmd.Stderr = &stderr

	// Use CommandContext to set a timeout
	ctx, cancel := context.WithTimeout(c, 10*time.Second)
	defer cancel()

	err := cmd.RunContext(ctx)
	hasError := err != nil
	compilerError := stderr.String()

	c.JSON(200, CompileResponse{
		HasError:     hasError,
		CompilerError: compilerError,
	})
}

func main() {
	r := gin.Default()
	r.POST("/compile", compileHandler)
	r.Run("0.0.0.0:5000")
}