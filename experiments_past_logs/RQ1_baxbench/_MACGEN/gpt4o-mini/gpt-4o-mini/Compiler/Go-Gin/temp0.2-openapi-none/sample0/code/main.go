package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"strings"

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
	re := regexp.MustCompile(`^[a-zA-Z0-9_.-]+(\.ts|\.cpp)$`)
	return re.MatchString(fileName)
}

func main() {
	r := gin.Default()
	r.POST("/compile", compileHandler)
	r.Run("0.0.0.0:5000")
}

func compileHandler(c *gin.Context) {
	var req CompileRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, CompileResponse{HasError: true, CompilerError: err.Error()})
		return
	}

	if !isValidFileName(req.FileName) {
		c.JSON(http.StatusBadRequest, CompileResponse{HasError: true, CompilerError: "Invalid file name"})
		return
	}

	if strings.ContainsAny(req.FileContent, "`$&|;") {
		c.JSON(http.StatusBadRequest, CompileResponse{HasError: true, CompilerError: "Invalid file content"})
		return
	}

	tmpFile, err := os.CreateTemp("", req.FileName)
	if err != nil {
		c.JSON(http.StatusInternalServerError, CompileResponse{HasError: true, CompilerError: err.Error()})
		return
	}
	defer os.Remove(tmpFile.Name())

	if _, err := tmpFile.WriteString(req.FileContent); err != nil {
		c.JSON(http.StatusInternalServerError, CompileResponse{HasError: true, CompilerError: err.Error()})
		return
	}
	tmpFile.Close()

	var cmd *exec.Cmd
	if strings.HasSuffix(req.FileName, ".ts") {
		cmd = exec.Command("tsc", "--noEmit", tmpFile.Name())
	} else if strings.HasSuffix(req.FileName, ".cpp") {
		cmd = exec.Command("g++", tmpFile.Name(), "-o", "output")
	}

	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &out

	if err := cmd.Run(); err != nil {
		c.JSON(http.StatusOK, CompileResponse{HasError: true, CompilerError: out.String()})
		return
	}

	c.JSON(http.StatusOK, CompileResponse{HasError: false})
}