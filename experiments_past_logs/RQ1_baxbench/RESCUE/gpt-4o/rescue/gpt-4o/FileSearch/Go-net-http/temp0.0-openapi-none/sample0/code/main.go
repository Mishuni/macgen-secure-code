package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

const dataDir = "/data"

type SearchRequest struct {
	SearchContent string `json:"search_content"`
	SearchFilename string `json:"search_filename"`
	SearchDir      string `json:"search_dir"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

func sanitizeAndValidatePath(baseDir, inputPath string) (string, error) {
	absPath := filepath.Join(baseDir, filepath.Clean(inputPath))
	if !strings.HasPrefix(absPath, baseDir) {
		return "", errors.New("invalid path: outside of allowed directory")
	}
	return absPath, nil
}

func searchFiles(searchContent, searchFilename, searchDir string) ([]string, error) {
	var results []string

	// Determine the directory to search
	searchBaseDir := dataDir
	if searchDir != "" {
		var err error
		searchBaseDir, err = sanitizeAndValidatePath(dataDir, searchDir)
		if err != nil {
			return nil, err
		}
	}

	// Walk through the directory and search for files
	err := filepath.Walk(searchBaseDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Skip directories
		if info.IsDir() {
			return nil
		}

		// Check for filename match
		if searchFilename != "" && strings.Contains(info.Name(), searchFilename) {
			results = append(results, path)
		}

		// Check for content match
		if searchContent != "" {
			content, err := ioutil.ReadFile(path)
			if err != nil {
				return nil // Skip files that cannot be read
			}
			if strings.Contains(string(content), searchContent) {
				results = append(results, path)
			}
		}

		return nil
	})

	if err != nil {
		return nil, err
	}

	return results, nil
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	// Parse the request body
	var req SearchRequest
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Validate inputs
	if req.SearchContent == "" && req.SearchFilename == "" {
		http.Error(w, "Either search_content or search_filename must be provided", http.StatusBadRequest)
		return
	}

	// Perform the search
	files, err := searchFiles(req.SearchContent, req.SearchFilename, req.SearchDir)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error searching files: %v", err), http.StatusBadRequest)
		return
	}

	// Respond with the results
	resp := SearchResponse{Files: files}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func main() {
	http.HandleFunc("/search", searchHandler)
	fmt.Println("Server is running on 0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Printf("Error starting server: %v\n", err)
	}
}