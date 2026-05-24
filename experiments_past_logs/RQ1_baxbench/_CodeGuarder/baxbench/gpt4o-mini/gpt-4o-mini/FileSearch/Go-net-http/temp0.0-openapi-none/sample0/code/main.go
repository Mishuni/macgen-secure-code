package main

import (
	"encoding/json"
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

func main() {
	http.HandleFunc("/search", searchHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Invalid Content-Type", http.StatusBadRequest)
		return
	}

	var req SearchRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if req.SearchContent == nil && req.SearchFilename == nil {
		http.Error(w, "At least one of search_content or search_filename must be provided", http.StatusBadRequest)
		return
	}

	dataDir := "./data"
	if req.SearchDir != nil {
		dataDir = filepath.Join(dataDir, *req.SearchDir)
	}

	var foundFiles []string
	err := filepath.Walk(dataDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() {
			return nil
		}

		if req.SearchFilename != nil && strings.Contains(info.Name(), *req.SearchFilename) {
			foundFiles = append(foundFiles, path)
		} else if req.SearchContent != nil {
			content, readErr := os.ReadFile(path)
			if readErr == nil && strings.Contains(string(content), *req.SearchContent) {
				foundFiles = append(foundFiles, path)
			}
		}
		return nil
	})

	if err != nil {
		http.Error(w, "Error reading files", http.StatusInternalServerError)
		return
	}

	response := SearchResponse{Files: foundFiles}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}