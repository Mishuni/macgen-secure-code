package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
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
	// Validate file name: only allow alphanumeric characters and a few safe symbols
	re := regexp.MustCompile(`^[a-zA-Z0-9_.-]+$`)
	return re.MatchString(fileName)
}

func compileCode(fileName, fileContent string) (bool, string) {
	if !isValidFileName(fileName) {
		return true, "Invalid file name."
	}

	// Create a temporary file to hold the code securely
	tmpFile, err := os.CreateTemp("", "source_*.tmp")
	if err != nil {
		return true, "Failed to create temporary file."
	}
	defer os.Remove(tmpFile.Name()) // Clean up the file afterwards

	// Write the file content to the temporary file
	if _, err := tmpFile.Write([]byte(fileContent)); err != nil {
		return true, "Failed to write to temporary file."
	}
	tmpFile.Close()

	// Determine the file extension
	ext := strings.ToLower(filepath.Ext(fileName))

	var cmd *exec.Cmd
	if ext == ".ts" {
		cmd = exec.Command("tsc", tmpFile.Name())
	} else if ext == ".cpp" {
		cmd = exec.Command("g++", tmpFile.Name(), "-o", "/tmp/output")
	} else {
		return true, "Unsupported file type."
	}

	// Run the compiler command
	output, err := cmd.CombinedOutput()
	if err != nil {
		return true, "Compilation error: " + string(output)
	}

	return false, ""
}

func compileHandler(w http.ResponseWriter, r *http.Request) {
	// Limit the size of the request body
	r.Body = http.MaxBytesReader(w, r.Body, 1<<20) // 1 MB limit
	var req CompileRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	hasError, compilerError := compileCode(req.FileName, req.FileContent)

	response := CompileResponse{
		HasError:      hasError,
		CompilerError: compilerError,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/compile", compileHandler)
	fmt.Println("Server is running on http://0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}