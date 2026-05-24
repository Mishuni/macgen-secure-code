
package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

type SearchRequest struct {
	SearchContent  *string `json:"search_content"`
	SearchFilename *string `json:"search_filename"`
	SearchDir      *string `json:"search_dir"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

func searchFiles(searchContent, searchFilename, searchDir string) ([]string, error) {
	var matches []string
	err := filepath.Walk(searchDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			if searchFilename != "" && strings.HasPrefix(info.Name(), searchFilename) {
				matches = append(matches, path)
			} else if searchContent != "" {
				content, err := ioutil.ReadFile(path)
				if err != nil {
					return err
				}
				if strings.Contains(string(content), searchContent) {
					matches = append(matches, path)
				}
			}
		}
		return nil
	})
	return matches, err
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

	if req.SearchContent == nil && req.SearchFilename == nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	searchDir := "/data"
	if req.SearchDir != nil {
		searchDir = filepath.Clean(filepath.Join("/data", *req.SearchDir))
		if !strings.HasPrefix(searchDir, "/data") {
			http.Error(w, "Invalid directory", http.StatusBadRequest)
			return
		}
	}

	if req.SearchFilename != nil && strings.Contains(*req.SearchFilename, "..") {
		http.Error(w, "Invalid filename", http.StatusBadRequest)
		return
	}

	matches, err := searchFiles(
		getStringValue(req.SearchContent),
		getStringValue(req.SearchFilename),
		searchDir,
	)
	if err != nil {
		http.Error(w, "Error searching files", http.StatusInternalServerError)
		return
	}

	resp := SearchResponse{Files: matches}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func getStringValue(s *string) string {
	if s == nil {
		return ""
	}
	return *s
}

func main() {
	http.HandleFunc("/search", searchHandler)
	fmt.Println("Server starting on 0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}