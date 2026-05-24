package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

type SearchRequest struct {
	SearchContent   *string `json:"search_content"`
	SearchFilename  *string `json:"search_filename"`
	SearchDir       *string `json:"search_dir"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

const maxFileSize = 1 << 20 // 1 MB
const baseDir = "./data"     // Base directory for file access

func main() {
	http.HandleFunc("/search", searchHandler)
	fmt.Println("Server is running on http://0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
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
	defer r.Body.Close()

	files, err := searchFiles(req.SearchContent, req.SearchFilename, req.SearchDir)
	if err != nil {
		http.Error(w, "Error searching files", http.StatusInternalServerError)
		return
	}

	response := SearchResponse{Files: files}
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(response); err != nil {
		http.Error(w, "Error encoding response", http.StatusInternalServerError)
	}
}

func searchFiles(content, filename, dir *string) ([]string, error) {
	var results []string
	dataDir := baseDir

	if dir != nil {
		// Validate the search directory
		if !isValidDir(*dir) {
			return nil, fmt.Errorf("invalid directory")
		}
		dataDir = filepath.Join(baseDir, *dir)
	}

	// Ensure the resolved path is within the base directory
	absDataDir, err := filepath.Abs(dataDir)
	if err != nil || !strings.HasPrefix(absDataDir, filepath.Join(baseDir, "")) {
		return nil, fmt.Errorf("directory access denied")
	}

	err = filepath.Walk(dataDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() {
			return nil
		}

		if filename != nil && strings.Contains(info.Name(), *filename) {
			results = append(results, path)
		} else if content != nil {
			if info.Size() > maxFileSize {
				return nil // Skip large files
			}
			fileContent, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			if strings.Contains(string(fileContent), *content) {
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

func isValidDir(dir string) bool {
	// Reject paths with ".." or any path separators
	if strings.Contains(dir, "..") || strings.ContainsAny(dir, "/\\") {
		return false
	}
	return true
}