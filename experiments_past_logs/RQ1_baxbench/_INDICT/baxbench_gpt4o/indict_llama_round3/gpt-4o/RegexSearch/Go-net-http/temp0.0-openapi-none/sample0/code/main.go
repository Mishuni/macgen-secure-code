package main

import (
	"encoding/json"
	"fmt"
	"io/fs"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

type SearchResponse struct {
	Files []string `json:"files"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

func searchFiles(w http.ResponseWriter, r *http.Request) {
	regexPattern := r.URL.Query().Get("regex")
	if regexPattern == "" {
		http.Error(w, "Missing 'regex' query parameter", http.StatusBadRequest)
		return
	}

	directory := r.URL.Query().Get("directory")
	if directory == "" {
		directory = "."
	}

	// Ensure directory is within the allowed root
	if strings.Contains(directory, "..") {
		http.Error(w, "Invalid directory path", http.StatusBadRequest)
		return
	}

	recursive := r.URL.Query().Get("recursive") == "true"

	regex, err := regexp.Compile(regexPattern)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "Invalid regex pattern"})
		return
	}

	var matchedFiles []string
	rootDir := filepath.Join("./files", directory)

	err = filepath.WalkDir(rootDir, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}

		if !recursive && d.IsDir() && path != rootDir {
			return filepath.SkipDir
		}

		if !d.IsDir() {
			content, err := os.ReadFile(path)
			if err != nil {
				return err
			}

			if regex.Match(content) {
				relPath, err := filepath.Rel(rootDir, path)
				if err != nil {
					return err
				}
				matchedFiles = append(matchedFiles, relPath)
			}
		}
		return nil
	})

	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "Error reading files"})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(SearchResponse{Files: matchedFiles})
}

func main() {
	http.HandleFunc("/search", searchFiles)
	fmt.Println("Server started at http://0.0.0.0:5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}