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
	FileName    string `json:"fileName" binding:"required"`
	FileContent string `json:"fileContent" binding:"required"`
}

type CompileResponse struct {
	HasError      bool   `json:"hasError"`
	CompilerError string `json:"compilerError,omitempty"`
}

func compileCode(fileName, fileContent string) (bool, string) {
	var cmd *exec.Cmd
	if fileName[len(fileName)-3:] == ".ts" {
		// Compile TypeScript
		cmd = exec.Command("tsc", fileName)
	} else if fileName[len(fileName)-4:] == ".cpp" {
		// Compile C++
		cmd = exec.Command("g++", fileName, "-o", "output")
	} else {
		return true, "Unsupported file type"
	}

	// Create a temporary file for the code
	tmpFile, err := exec.Command("bash", "-c", fmt.Sprintf("echo '%s' > %s", fileContent, fileName)).Output()
	if err != nil {
		return true, "Failed to write temporary file"
	}

	// Run the compilation command
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
	if err := r.Run("0.0.0.0:5000"); err != nil {
		panic(err)
	}
}