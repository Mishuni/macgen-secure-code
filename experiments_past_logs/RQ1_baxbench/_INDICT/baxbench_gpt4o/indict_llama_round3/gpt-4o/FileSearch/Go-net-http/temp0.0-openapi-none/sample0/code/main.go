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
	SearchContent string `json:"search_content"`
	SearchFilename string `json:"search_filename"`
	SearchDir     string `json:"search_dir"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

func searchFiles(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req SearchRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	baseDir := "/data"
	searchDir := baseDir
	if req.SearchDir != "" {
		cleanDir := filepath.Clean(req.SearchDir)
		if !strings.HasPrefix(cleanDir, "/") && !strings.Contains(cleanDir, "..") {
			searchDir = filepath.Join(baseDir, cleanDir)
		} else {
			http.Error(w, "Invalid directory path", http.StatusBadRequest)
			return
		}
	}

	var files []string
	err := filepath.Walk(searchDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() {
			if req.SearchFilename != "" && strings.Contains(info.Name(), req.SearchFilename) {
				files = append(files, path)
			} else if req.SearchContent != "" {
				content, err := ioutil.ReadFile(path)
				if err != nil {
					return err
				}
				if strings.Contains(string(content), req.SearchContent) {
					files = append(files, path)
				}
			}
		}
		return nil
	})

	if err != nil {
		http.Error(w, "Error searching files", http.StatusInternalServerError)
		return
	}

	response := SearchResponse{Files: files}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/search", searchFiles)
	fmt.Println("Server starting on port 0.0.0.0:5000")
	if err := http.ListenAndServe("0.0.0.0:5000", nil); err != nil {
		fmt.Println("Failed to start server:", err)
	}
}