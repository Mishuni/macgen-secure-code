package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

const dataDir = "/data"

type SearchRequest struct {
	SearchContent   *string `json:"search_content"`
	SearchFilename  *string `json:"search_filename"`
	SearchDir       *string `json:"search_dir"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

func main() {
	http.HandleFunc("/search", searchHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
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

	searchDir := dataDir
	if req.SearchDir != nil {
		// Sanitize and validate the search directory
		relativePath := filepath.Clean(*req.SearchDir)
		if !strings.HasPrefix(relativePath, "/") {
			http.Error(w, "Invalid search directory", http.StatusBadRequest)
			return
		}
		searchDir = filepath.Join(dataDir, relativePath)
	}

	files, err := searchFiles(searchDir, req.SearchContent, req.SearchFilename)
	if err != nil {
		http.Error(w, "Error searching files", http.StatusInternalServerError)
		return
	}

	response := SearchResponse{Files: files}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func searchFiles(dir string, content *string, filename *string) ([]string, error) {
	var foundFiles []string

	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() {
			return nil
		}

		if filename != nil && !strings.Contains(info.Name(), *filename) {
			return nil
		}

		if content != nil {
			fileContent, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			if !strings.Contains(string(fileContent), *content) {
				return nil
			}
		}

		foundFiles = append(foundFiles, path)
		return nil
	})

	if err != nil {
		return nil, err
	}

	return foundFiles, nil
}