package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
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

func compileCode(fileName, fileContent string) (bool, string) {
	// Validate file name
	if !isValidFileName(fileName) {
		return true, "Invalid file name."
	}

	// Create a temporary file for the code
	tmpFile, err := ioutil.TempFile("", "code-*.tmp")
	if err != nil {
		return true, "Failed to create temporary file."
	}
	defer os.Remove(tmpFile.Name()) // Ensure the temporary file is removed

	// Write the file content to the temporary file
	if _, err := tmpFile.WriteString(fileContent); err != nil {
		return true, "Failed to write to temporary file."
	}
	tmpFile.Close() // Close the file to flush the content

	// Determine the file extension
	ext := filepath.Ext(fileName)

	var cmd *exec.Cmd
	if ext == ".ts" {
		cmd = exec.Command("tsc", tmpFile.Name())
	} else if ext == ".cpp" {
		cmd = exec.Command("g++", tmpFile.Name(), "-o", "/tmp/output")
	} else {
		return true, "Unsupported file type."
	}

	// Run the compilation command
	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &out
	err = cmd.Run()

	if err != nil {
		return true, "Compilation error: " + out.String()
	}
	return false, ""
}

// isValidFileName checks if the provided file name is valid
func isValidFileName(fileName string) bool {
	// Check for invalid characters and length
	if len(fileName) == 0 || len(fileName) > 255 {
		return false
	}
	// Allow only alphanumeric characters, underscores, and dots
	validFileName := regexp.MustCompile(`^[a-zA-Z0-9_.]+$`)
	return validFileName.MatchString(fileName)
}

func compileHandler(c *gin.Context) {
	var req CompileRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, CompileResponse{HasError: true, CompilerError: "Invalid request format."})
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