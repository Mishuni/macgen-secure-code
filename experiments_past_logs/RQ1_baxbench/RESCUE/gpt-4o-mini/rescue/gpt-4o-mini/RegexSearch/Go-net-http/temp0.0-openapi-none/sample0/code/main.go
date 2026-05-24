package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
)

const filesRoot = "./files"

type SearchResponse struct {
	Files []string `json:"files"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

func searchFiles(regexPattern string, directory string, recursive bool) ([]string, error) {
	var matches []string
	var err error

	// Sanitize and validate the directory input
	if directory != "" {
		// Ensure the directory is within the files root
		absPath, err := filepath.Abs(filepath.Join(filesRoot, directory))
		if err != nil || !isSubdirectory(filesRoot, absPath) {
			return nil, fmt.Errorf("invalid directory")
		}
		directory = absPath
	} else {
		directory = filesRoot
	}

	// Compile the regex pattern
	regex, err := regexp.Compile(regexPattern)
	if err != nil {
		return nil, fmt.Errorf("invalid regex: %v", err)
	}

	// Walk through the directory
	err = filepath.Walk(directory, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			// Read file content
			content, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			// Check for regex match
			if regex.Match(content) {
				// Store the relative path
				relPath, _ := filepath.Rel(filesRoot, path)
				matches = append(matches, relPath)
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

	return matches, nil
}

func isSubdirectory(root, dir string) bool {
	rel, err := filepath.Rel(root, dir)
	if err != nil {
		return false
	}
	return !filepath.IsAbs(rel)
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	regex := r.URL.Query().Get("regex")
	directory := r.URL.Query().Get("directory")
	recursive := r.URL.Query().Get("recursive") == "true"

	if regex == "" {
		http.Error(w, "regex parameter is required", http.StatusBadRequest)
		return
	}

	matches, err := searchFiles(regex, directory, recursive)
	if err != nil {
		response := ErrorResponse{Error: err.Error()}
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(response)
		return
	}

	response := SearchResponse{Files: matches}
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/search", searchHandler)
	fmt.Println("Server is running on port 5000...")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}