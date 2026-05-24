package main

import (
	"bytes"
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
	HasError      bool   `json:"hasError"`
	CompilerError string `json:"compilerError,omitempty"`
}

func sanitizeInput(input string) string {
	// Allow only alphanumeric characters, dots, underscores, and hyphens
	return strings.Map(func(r rune) rune {
		if (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9') || r == '.' || r == '_' || r == '-' {
			return r
		}
		return -1
	}, input)
}

func compileCode(w http.ResponseWriter, r *http.Request) {
	var req CompileRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	// Sanitize inputs
	req.FileName = sanitizeInput(req.FileName)
	req.FileContent = sanitizeInput(req.FileContent)

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
	var stderr bytes.Buffer
	cmd.Stderr = &stderr

	err := cmd.Run()
	response := CompileResponse{
		HasError:      err != nil,
		CompilerError: "Compilation error occurred", // Generic error message
	}

	if err != nil {
		fmt.Println("Error:", stderr.String()) // Log detailed error server-side
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/compile", compileCode)
	fmt.Println("Server started at 0.0.0.0:5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}