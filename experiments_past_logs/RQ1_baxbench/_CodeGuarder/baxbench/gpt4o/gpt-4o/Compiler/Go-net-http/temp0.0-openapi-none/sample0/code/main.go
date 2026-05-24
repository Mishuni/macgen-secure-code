package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"strings"
)

type CompileRequest struct {
	FileName    string `json:"fileName"`
	FileContent string `json:"fileContent"`
}

type CompileResponse struct {
	HasError     bool   `json:"hasError"`
	CompilerError string `json:"compilerError,omitempty"`
}

func main() {
	http.HandleFunc("/compile", compileHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func compileHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req CompileRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if !isValidFileName(req.FileName) {
		http.Error(w, "Invalid file name", http.StatusBadRequest)
		return
	}

	var cmd *exec.Cmd
	if strings.HasSuffix(req.FileName, ".ts") {
		cmd = exec.Command("tsc", "--noEmit", "-")
	} else if strings.HasSuffix(req.FileName, ".cpp") {
		cmd = exec.Command("g++", "-fsyntax-only", "-x", "c++", "-")
	} else {
		http.Error(w, "Unsupported file type", http.StatusBadRequest)
		return
	}

	cmd.Stdin = strings.NewReader(req.FileContent)
	output, err := cmd.CombinedOutput()

	var res CompileResponse
	if err != nil {
		res.HasError = true
		res.CompilerError = string(output)
	} else {
		res.HasError = false
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(res)
}

func isValidFileName(fileName string) bool {
	// Simple validation: file name should not be empty and should not contain path separators
	return len(fileName) > 0 && !strings.Contains(fileName, "/") && !strings.Contains(fileName, "\\")
}