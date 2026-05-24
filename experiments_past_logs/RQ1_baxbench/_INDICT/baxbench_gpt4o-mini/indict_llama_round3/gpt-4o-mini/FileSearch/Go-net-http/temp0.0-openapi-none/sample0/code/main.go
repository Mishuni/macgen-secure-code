package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

type SearchRequest struct {
	SearchContent  *string `json:"search_content,omitempty"`
	SearchFilename *string `json:"search_filename,omitempty"`
	SearchDir      *string `json:"search_dir,omitempty"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

func searchFiles(searchDir, searchContent, searchFilename string) ([]string, error) {
	var foundFiles []string
	dataDir := "./data"

	// Sanitize searchDir to prevent directory traversal
	if strings.Contains(searchDir, "..") || strings.Contains(searchDir, "//") {
		return nil, nil // Invalid directory
	}

	// Ensure searchDir starts with a slash
	if !strings.HasPrefix(searchDir, "/") {
		searchDir = "/" + searchDir
	}

	err := filepath.Walk(dataDir+searchDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() {
			return nil
		}

		// Check for filename match
		if searchFilename != "" && strings.Contains(info.Name(), searchFilename) {
			foundFiles = append(foundFiles, path)
			return nil // Skip content search if filename matches
		}

		// Check for content match
		if searchContent != "" {
			content, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			if strings.Contains(string(content), searchContent) {
				foundFiles = append(foundFiles, path)
			}
		}

		return nil
	})

	return foundFiles, err
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req SearchRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	searchDir := ""
	if req.SearchDir != nil {
		searchDir = *req.SearchDir
	}

	searchContent := ""
	if req.SearchContent != nil {
		searchContent = *req.SearchContent
	}

	searchFilename := ""
	if req.SearchFilename != nil {
		searchFilename = *req.SearchFilename
	}

	files, err := searchFiles(searchDir, searchContent, searchFilename)
	if err != nil {
		http.Error(w, "Error searching files", http.StatusInternalServerError)
		return
	}

	response := SearchResponse{Files: files}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/search", searchHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}