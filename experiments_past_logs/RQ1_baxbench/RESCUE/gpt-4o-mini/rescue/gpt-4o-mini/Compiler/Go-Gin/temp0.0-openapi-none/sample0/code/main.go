package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"

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
	// Create a temporary file for the code
	tmpFile, err := exec.Command("mktemp", "/tmp/XXXXXX").Output()
	if err != nil {
		return true, "Failed to create temporary file"
	}

	// Write the file content to the temporary file
	if err := exec.Command("bash", "-c", fmt.Sprintf("echo '%s' > %s", fileContent, string(tmpFile))).Run(); err != nil {
		return true, "Failed to write to temporary file"
	}

	// Determine the file extension
	var cmd *exec.Cmd
	if fileName[len(fileName)-3:] == ".ts" {
		cmd = exec.Command("tsc", string(tmpFile))
	} else if fileName[len(fileName)-4:] == ".cpp" {
		cmd = exec.Command("g++", string(tmpFile), "-o", "/tmp/output")
	} else {
		return true, "Unsupported file type"
	}

	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &out

	// Run the compiler command
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