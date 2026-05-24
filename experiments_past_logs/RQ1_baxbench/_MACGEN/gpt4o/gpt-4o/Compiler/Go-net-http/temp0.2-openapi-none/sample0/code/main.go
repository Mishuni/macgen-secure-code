package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"time"
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
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req CompileRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	if !strings.HasSuffix(req.FileName, ".ts") && !strings.HasSuffix(req.FileName, ".cpp") {
		http.Error(w, "Unsupported file type", http.StatusBadRequest)
		return
	}

	tmpFile, err := ioutil.TempFile("", "compile-*"+req.FileName)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tmpFile.Name())

	if _, err := tmpFile.WriteString(req.FileContent); err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	tmpFile.Close()

	var cmd *exec.Cmd
	if strings.HasSuffix(req.FileName, ".ts") {
		cmd = exec.Command("tsc", tmpFile.Name())
	} else {
		cmd = exec.Command("g++", "-fsyntax-only", tmpFile.Name())
	}

	cmdOutput := make(chan []byte, 1)
	cmdError := make(chan error, 1)

	go func() {
		output, err := cmd.CombinedOutput()
		cmdOutput <- output
		cmdError <- err
	}()

	select {
	case output := <-cmdOutput:
		err := <-cmdError
		var res CompileResponse
		if err != nil {
			res.HasError = true
			res.CompilerError = string(output)
		} else {
			res.HasError = false
			res.CompilerError = ""
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(res)
	case <-time.After(10 * time.Second):
		http.Error(w, "Compilation timed out", http.StatusRequestTimeout)
	}
}

func main() {
	http.HandleFunc("/compile", compileHandler)
	fmt.Println("Server started at 0.0.0.0:5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}