package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

const filesRoot = "./files"

type searchResponse struct {
	Files []string `json:"files"`
}

type errorResponse struct {
	Error string `json:"error"`
}

func main() {
	http.HandleFunc("/search", searchHandler)
	fmt.Println("Starting server on 0.0.0.0:5000...")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Printf("Error starting server: %v\n", err)
	}
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Parse query parameters
	regexPattern := r.URL.Query().Get("regex")
	if regexPattern == "" {
		writeErrorResponse(w, http.StatusBadRequest, "Missing required 'regex' parameter")
		return
	}

	directory := r.URL.Query().Get("directory")
	if directory == "" {
		directory = "."
	}

	recursive := r.URL.Query().Get("recursive") == "true"

	// Validate and compile regex
	regex, err := regexp.Compile(regexPattern)
	if err != nil {
		writeErrorResponse(w, http.StatusBadRequest, "Invalid regex pattern")
		return
	}

	// Construct the full directory path
	searchDir := filepath.Join(filesRoot, filepath.Clean(directory))
	if !strings.HasPrefix(searchDir, filesRoot) {
		writeErrorResponse(w, http.StatusBadRequest, "Invalid directory path")
		return
	}

	// Search for matching files
	files, err := searchFiles(searchDir, regex, recursive)
	if err != nil {
		writeErrorResponse(w, http.StatusInternalServerError, err.Error())
		return
	}

	// Respond with the list of matching files
	response := searchResponse{Files: files}
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(response); err != nil {
		writeErrorResponse(w, http.StatusInternalServerError, "Failed to encode response")
	}
}

func searchFiles(dir string, regex *regexp.Regexp, recursive bool) ([]string, error) {
	var matchingFiles []string

	// Walk through the directory
	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Skip directories unless recursive is true
		if info.IsDir() {
			if !recursive && path != dir {
				return filepath.SkipDir
			}
			return nil
		}

		// Read file content
		content, err := ioutil.ReadFile(path)
		if err != nil {
			return err
		}

		// Check if the file content matches the regex
		if regex.Match(content) {
			relativePath, err := filepath.Rel(dir, path)
			if err != nil {
				return err
			}
			matchingFiles = append(matchingFiles, relativePath)
		}

		return nil
	})

	if err != nil {
		return nil, err
	}

	return matchingFiles, nil
}

func writeErrorResponse(w http.ResponseWriter, statusCode int, message string) {
	w.WriteHeader(statusCode)
	w.Header().Set("Content-Type", "application/json")
	response := errorResponse{Error: message}
	_ = json.NewEncoder(w).Encode(response)
}