package main

import (
	"encoding/json"
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

func validDir(searchDir string) bool {
	// Allow only specific directories (e.g., "songs", "documents")
	allowedDirs := map[string]struct{}{
		"songs":     {},
		"documents": {},
	}
	_, valid := allowedDirs[searchDir]
	return valid
}

func searchFiles(searchDir string, searchContent *string, searchFilename *string) ([]string, error) {
	var matchedFiles []string

	err := filepath.Walk(filepath.Join("data", searchDir), func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() {
			return nil
		}

		if searchFilename != nil && strings.Contains(info.Name(), *searchFilename) {
			matchedFiles = append(matchedFiles, filepath.Base(path))
		}

		if searchContent != nil {
			content, err := ioutil.ReadFile(path)
			if err != nil {
				return err
			}
			if strings.Contains(string(content), *searchContent) {
				matchedFiles = append(matchedFiles, filepath.Base(path))
			}
		}

		return nil
	})

	return matchedFiles, err
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	var req SearchRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if req.SearchDir == nil || !validDir(*req.SearchDir) {
		http.Error(w, "Invalid directory", http.StatusBadRequest)
		return
	}

	matchedFiles, err := searchFiles(*req.SearchDir, req.SearchContent, req.SearchFilename)
	if err != nil {
		http.Error(w, "Error searching files", http.StatusInternalServerError)
		return
	}

	response := SearchResponse{Files: matchedFiles}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/search", searchHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}