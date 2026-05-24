package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
)

const baseDir = "./files"

type SearchResponse struct {
	Files []string `json:"files"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

func main() {
	http.HandleFunc("/search", searchHandler)
	fmt.Println("Server is running on http://0.0.0.0:5000/search")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	regexStr := r.URL.Query().Get("regex")
	directory := r.URL.Query().Get("directory")
	recursive := r.URL.Query().Get("recursive")

	if regexStr == "" {
		http.Error(w, "Missing 'regex' parameter", http.StatusBadRequest)
		return
	}

	if directory == "" {
		directory = baseDir
	} else {
		directory = filepath.Join(baseDir, directory)
	}

	if !isValidDirectory(directory) {
		http.Error(w, "Invalid directory", http.StatusBadRequest)
		return
	}

	files, err := searchFiles(directory, regexStr, recursive == "true")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	response := SearchResponse{Files: files}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func isValidDirectory(dir string) bool {
	absPath, err := filepath.Abs(dir)
	if err != nil {
		return false
	}
	baseAbsPath, err := filepath.Abs(baseDir)
	if err != nil {
		return false
	}
	return filepath.HasPrefix(absPath, baseAbsPath)
}

func searchFiles(directory, regexStr string, recursive bool) ([]string, error) {
	var matchingFiles []string
	re, err := regexp.Compile(regexStr)
	if err != nil {
		return nil, fmt.Errorf("invalid regex: %v", err)
	}

	err = filepath.Walk(directory, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			content, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			if re.Match(content) {
				relPath, _ := filepath.Rel(baseDir, path)
				matchingFiles = append(matchingFiles, relPath)
			}
		}
		if !recursive && info.IsDir() {
			return filepath.SkipDir
		}
		return nil
	})

	if err != nil {
		return nil, err
	}
	return matchingFiles, nil
}