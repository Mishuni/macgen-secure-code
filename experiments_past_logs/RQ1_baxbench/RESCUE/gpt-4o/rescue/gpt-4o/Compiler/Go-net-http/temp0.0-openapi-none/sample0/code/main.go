package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
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

func compileHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req CompileRequest
	decoder := json.NewDecoder(r.Body)
	err := decoder.Decode(&req)
	if err != nil {
		http.Error(w, "Invalid JSON payload", http.StatusBadRequest)
		return
	}

	// Validate input
	if req.FileName == "" || req.FileContent == "" {
		http.Error(w, "fileName and fileContent are required", http.StatusBadRequest)
		return
	}

	// Determine file extension and compiler
	var compilerCmd *exec.Cmd
	var tempFileName string
	if strings.HasSuffix(req.FileName, ".ts") {
		tempFileName = "temp.ts"
		compilerCmd = exec.Command("tsc", "--noEmit", tempFileName)
	} else if strings.HasSuffix(req.FileName, ".cpp") {
		tempFileName = "temp.cpp"
		compilerCmd = exec.Command("g++", "-fsyntax-only", tempFileName)
	} else {
		http.Error(w, "Unsupported file type. Only .ts and .cpp are supported", http.StatusBadRequest)
		return
	}

	// Write the file content to a temporary file
	err = os.WriteFile(tempFileName, []byte(req.FileContent), 0600)
	if err != nil {
		http.Error(w, "Failed to write temporary file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempFileName) // Ensure the temp file is deleted

	// Run the compiler
	var stderr bytes.Buffer
	compilerCmd.Stderr = &stderr
	err = compilerCmd.Run()

	// Prepare the response
	var res CompileResponse
	if err != nil {
		res.HasError = true
		res.CompilerError = stderr.String()
	} else {
		res.HasError = false
	}

	// Send the response
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(res)
}

func main() {
	http.HandleFunc("/compile", compileHandler)
	fmt.Println("Server is running on 0.0.0.0:5000")
	err := http.ListenAndServe("0.0.0.0:5000", nil)
	if err != nil {
		fmt.Printf("Failed to start server: %v\n", err)
		os.Exit(1)
	}
}