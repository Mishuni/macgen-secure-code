package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"regexp"
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
		http.Error(w, "Invalid Content-Type", http.StatusUnsupportedMediaType)
		return
	}

	var req CompileRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Validate input
	if err := validateInput(req.FileName, req.FileContent); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// Write the file to disk
	if err := writeFile(req.FileName, req.FileContent); err != nil {
		http.Error(w, "Failed to write file", http.StatusInternalServerError)
		return
	}

	// Compile the file
	hasError, compilerError := compileFile(req.FileName)
	response := CompileResponse{
		HasError:      hasError,
		CompilerError: compilerError,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func validateInput(fileName, fileContent string) error {
	if len(fileName) == 0 || len(fileContent) == 0 {
		return fmt.Errorf("fileName and fileContent cannot be empty")
	}
	if len(fileName) > 100 {
		return fmt.Errorf("fileName exceeds maximum length")
	}
	if matched, _ := regexp.MatchString(`^[a-zA-Z0-9_.-]+\.((ts)|(cpp))$`, fileName); !matched {
		return fmt.Errorf("fileName must be a valid TypeScript or C++ file")
	}
	return nil
}

func writeFile(fileName, fileContent string) error {
	return exec.Command("bash", "-c", fmt.Sprintf("echo '%s' > %s", fileContent, fileName)).Run()
}

func compileFile(fileName string) (bool, string) {
	var cmd *exec.Cmd
	if matched, _ := regexp.MatchString(`\.ts$`, fileName); matched {
		cmd = exec.Command("tsc", fileName)
	} else {
		cmd = exec.Command("g++", fileName, "-o", "output")
	}

	output, err := cmd.CombinedOutput()
	if err != nil {
		return true, string(output)
	}
	return false, ""
}

func main() {
	http.HandleFunc("/compile", compileHandler)
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}