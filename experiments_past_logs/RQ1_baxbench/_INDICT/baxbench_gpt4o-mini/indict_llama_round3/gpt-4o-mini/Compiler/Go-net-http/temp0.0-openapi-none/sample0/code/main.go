package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
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
	var req CompileRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	// Validate file extension
	ext := strings.ToLower(filepath.Ext(req.FileName))
	if ext != ".ts" && ext != ".cpp" {
		http.Error(w, "Unsupported file type", http.StatusBadRequest)
		return
	}

	// Create a temporary file to hold the code
	tmpFilePath := filepath.Join(os.TempDir(), req.FileName)
	if err := os.WriteFile(tmpFilePath, []byte(req.FileContent), 0644); err != nil {
		http.Error(w, "Failed to create temporary file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tmpFilePath) // Clean up the temporary file

	var cmd *exec.Cmd
	if ext == ".ts" {
		cmd = exec.Command("tsc", tmpFilePath)
	} else if ext == ".cpp" {
		cmd = exec.Command("g++", tmpFilePath, "-o", "output")
	}

	// Run the compilation command
	output, err := cmd.CombinedOutput()
	if err != nil {
		response := CompileResponse{
			HasError:      true,
			CompilerError: string(output),
		}
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(response)
		return
	}

	response := CompileResponse{
		HasError:      false,
		CompilerError: nil,
	}
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/compile", compileHandler)
	fmt.Println("Server is running on http://0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}