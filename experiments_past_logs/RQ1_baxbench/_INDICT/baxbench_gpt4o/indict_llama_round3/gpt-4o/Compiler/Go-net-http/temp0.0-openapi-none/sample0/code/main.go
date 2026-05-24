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
	HasError     bool   `json:"hasError"`
	CompilerError string `json:"compilerError"`
}

func compileHandler(w http.ResponseWriter, r *http.Request) {
	var req CompileRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	var cmd *exec.Cmd
	var fileExt string

	if strings.HasSuffix(req.FileName, ".ts") {
		fileExt = ".ts"
		cmd = exec.Command("tsc", "--noEmit")
	} else if strings.HasSuffix(req.FileName, ".cpp") {
		fileExt = ".cpp"
		cmd = exec.Command("g++", "-fsyntax-only")
	} else {
		http.Error(w, "Unsupported file type", http.StatusBadRequest)
		return
	}

	tmpFile, err := os.CreateTemp("", fmt.Sprintf("tempfile-*%s", fileExt))
	if err != nil {
		http.Error(w, "Could not create temporary file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tmpFile.Name())

	if _, err := tmpFile.Write([]byte(req.FileContent)); err != nil {
		http.Error(w, "Could not write to temporary file", http.StatusInternalServerError)
		return
	}
	tmpFile.Close()

	cmd.Args = append(cmd.Args, tmpFile.Name())

	var stderr bytes.Buffer
	cmd.Stderr = &stderr

	err = cmd.Run()

	var res CompileResponse
	if err != nil {
		res.HasError = true
		res.CompilerError = stderr.String()
	} else {
		res.HasError = false
		res.CompilerError = ""
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(res)
}

func main() {
	http.HandleFunc("/compile", compileHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}