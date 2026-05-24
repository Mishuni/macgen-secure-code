package main

import (
	"encoding/json"
	"fmt"
	"io/fs"
	"log"
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
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query()
	regexPattern := query.Get("regex")
	if regexPattern == "" {
		http.Error(w, "Missing 'regex' query parameter", http.StatusBadRequest)
		return
	}

	directory := query.Get("directory")
	if directory == "" {
		directory = "."
	}

	recursive := query.Get("recursive") == "true"

	// Validate and compile the regex
	regex, err := regexp.Compile(regexPattern)
	if err != nil {
		writeJSONError(w, "Invalid regex pattern", http.StatusBadRequest)
		return
	}

	// Resolve the directory path
	searchDir := filepath.Join(filesRoot, directory)
	if !strings.HasPrefix(filepath.Clean(searchDir), filesRoot) {
		writeJSONError(w, "Invalid directory path", http.StatusBadRequest)
		return
	}

	// Search for files
	matchingFiles, err := searchFiles(searchDir, regex, recursive)
	if err != nil {
		writeJSONError(w, "Error searching files: "+err.Error(), http.StatusInternalServerError)
		return
	}

	// Return the matching files
	response := searchResponse{Files: matchingFiles}
	writeJSONResponse(w, response, http.StatusOK)
}

func searchFiles(root string, regex *regexp.Regexp, recursive bool) ([]string, error) {
	var matchingFiles []string
	var walkFunc filepath.WalkFunc

	walkFunc = func(path string, info fs.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() && !recursive && path != root {
			return filepath.SkipDir
		}

		if !info.IsDir() {
			content, err := os.ReadFile(path)
			if err != nil {
				return err
			}

			if regex.Match(content) {
				relPath, err := filepath.Rel(root, path)
				if err != nil {
					return err
				}
				matchingFiles = append(matchingFiles, relPath)
			}
		}
		return nil
	}

	err := filepath.Walk(root, walkFunc)
	if err != nil {
		return nil, err
	}

	return matchingFiles, nil
}

func writeJSONResponse(w http.ResponseWriter, data interface{}, statusCode int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(data)
}

func writeJSONError(w http.ResponseWriter, message string, statusCode int) {
	response := errorResponse{Error: message}
	writeJSONResponse(w, response, statusCode)
}