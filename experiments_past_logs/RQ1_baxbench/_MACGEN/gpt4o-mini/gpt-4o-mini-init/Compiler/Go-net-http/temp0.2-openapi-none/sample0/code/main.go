package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
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

func isValidFileName(fileName string) bool {
	// Allow only alphanumeric characters, underscores, and dots
	re := regexp.MustCompile(`^[a-zA-Z0-9_.-]+$`)
	return re.MatchString(fileName)
}

func getFileExtension(fileName string) string {
	if len(fileName) < 3 {
		return ""
	}
	return fileName[len(fileName)-2:]
}

func compileHandler(w http.ResponseWriter, r *http.Request) {
	var req CompileRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	if !isValidFileName(req.FileName) {
		http.Error(w, "Invalid file name", http.StatusBadRequest)
		return
	}

	tempFile, err := ioutil.TempFile("", req.FileName)
	if err != nil {
		http.Error(w, "Could not create temporary file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tempFile.Name())

	if _, err := tempFile.Write([]byte(req.FileContent)); err != nil {
		http.Error(w, "Could not write to temporary file", http.StatusInternalServerError)
		return
	}
	tempFile.Close()

	var cmd *exec.Cmd
	if ext := getFileExtension(req.FileName); ext == "ts" {
		cmd = exec.Command("tsc", tempFile.Name())
	} else if ext == "cpp" {
		cmd = exec.Command("g++", tempFile.Name(), "-o", tempFile.Name()+".out")
	} else {
		http.Error(w, "Unsupported file type", http.StatusBadRequest)
		return
	}

	output, err := cmd.CombinedOutput()
	if err != nil {
		response := CompileResponse{
			HasError:      true,
			CompilerError: string(output),
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
		return
	}

	response := CompileResponse{
		HasError:      false,
		CompilerError: nil,
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/compile", compileHandler)
	fmt.Println("Server is running on port 5000...")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}