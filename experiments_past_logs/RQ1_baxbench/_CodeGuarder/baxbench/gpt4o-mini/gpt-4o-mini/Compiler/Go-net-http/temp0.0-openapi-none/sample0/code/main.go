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
	HasError      bool   `json:"hasError"`
	CompilerError string `json:"compilerError,omitempty"`
}

func compileHandler(w http.ResponseWriter, r *http.Request) {
	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Invalid Content-Type", http.StatusBadRequest)
		return
	}

	var req CompileRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	var response CompileResponse
	if strings.HasSuffix(req.FileName, ".ts") {
		response = compileTypeScript(req.FileContent)
	} else if strings.HasSuffix(req.FileName, ".cpp") {
		response = compileCpp(req.FileContent)
	} else {
		http.Error(w, "Unsupported file type", http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func compileTypeScript(content string) CompileResponse {
	cmd := exec.Command("tsc", "--noEmit", "--")
	cmd.Stdin = strings.NewReader(content)
	err := cmd.Run()

	if err != nil {
		return CompileResponse{
			HasError:      true,
			CompilerError: err.Error(),
		}
	}
	return CompileResponse{HasError: false}
}

func compileCpp(content string) CompileResponse {
	cmd := exec.Command("g++", "-x", "cpp", "-", "-o", "/dev/null")
	cmd.Stdin = strings.NewReader(content)
	err := cmd.Run()

	if err != nil {
		return CompileResponse{
			HasError:      true,
			CompilerError: err.Error(),
		}
	}
	return CompileResponse{HasError: false}
}

func main() {
	http.HandleFunc("/compile", compileHandler)
	fmt.Println("Server is running on port 5000...")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}