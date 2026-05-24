package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"

	"github.com/gin-gonic/gin"
)

type CompileRequest struct {
	FileName    string `json:"fileName"`
	FileContent string `json:"fileContent"`
}

type CompileResponse struct {
	HasError      bool   `json:"hasError"`
	CompilerError string `json:"compilerError,omitempty"`
}

func isValidFileName(fileName string) bool {
	// Validate the file name to prevent command injection
	validFileName := regexp.MustCompile(`^[a-zA-Z0-9._-]+$`)
	return validFileName.MatchString(fileName)
}

func compileCode(fileName, fileContent string) (bool, string) {
	if !isValidFileName(fileName) {
		return true, "Invalid file name"
	}

	// Create a temporary directory
	tmpDir, err := os.MkdirTemp("", "compiler")
	if err != nil {
		return true, "Error creating temporary directory"
	}
	defer os.RemoveAll(tmpDir) // Clean up the temporary directory

	// Create a temporary file for the code
	tmpFilePath := filepath.Join(tmpDir, fileName)
	if err := os.WriteFile(tmpFilePath, []byte(fileContent), 0644); err != nil {
		return true, "Error writing to temporary file"
	}

	var cmd *exec.Cmd
	if filepath.Ext(fileName) == ".ts" {
		// Compile TypeScript
		cmd = exec.Command("tsc", "--noEmit", tmpFilePath)
	} else if filepath.Ext(fileName) == ".cpp" {
		// Compile C++
		cmd = exec.Command("g++", tmpFilePath, "-o", filepath.Join(tmpDir, "output"))
	} else {
		return true, "Unsupported file type"
	}

	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &out
	err = cmd.Run()
	if err != nil {
		return true, out.String()
	}
	return false, ""
}

func compileHandler(c *gin.Context) {
	var req CompileRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, CompileResponse{HasError: true, CompilerError: "Invalid request"})
		return
	}

	hasError, compilerError := compileCode(req.FileName, req.FileContent)
	c.JSON(http.StatusOK, CompileResponse{HasError: hasError, CompilerError: compilerError})
}

func main() {
	r := gin.Default()
	r.POST("/compile", compileHandler)
	r.Run("0.0.0.0:5000")
}