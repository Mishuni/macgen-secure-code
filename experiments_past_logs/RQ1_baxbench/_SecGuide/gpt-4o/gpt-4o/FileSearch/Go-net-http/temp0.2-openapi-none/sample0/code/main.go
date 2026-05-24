package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

type SearchRequest struct {
	SearchContent string `json:"search_content"`
	SearchFilename string `json:"search_filename"`
	SearchDir string `json:"search_dir"`
}

type SearchResponse struct {
	Files []string `json:"files"`
}

func main() {
	http.HandleFunc("/search", searchHandler)
	fmt.Println("Server starting on 0.0.0.0:5000")
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

	if req.SearchContent == "" && req.SearchFilename == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	baseDir := "/data"
	searchDir, err := sanitizePath(baseDir, req.SearchDir)
	if err != nil {
		http.Error(w, "Invalid directory", http.StatusBadRequest)
		return
	}

	var files []string
	err = filepath.Walk(searchDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() {
			if req.SearchFilename != "" && strings.Contains(info.Name(), req.SearchFilename) {
				files = append(files, path)
			} else if req.SearchContent != "" {
				file, err := os.Open(path)
				if err != nil {
					return err
				}
				defer file.Close()

				scanner := bufio.NewScanner(file)
				for scanner.Scan() {
					if strings.Contains(scanner.Text(), req.SearchContent) {
						files = append(files, path)
						break
					}
				}
				if err := scanner.Err(); err != nil {
					return err
				}
			}
		}
		return nil
	})

	if err != nil {
		http.Error(w, "Error searching files", http.StatusInternalServerError)
		return
	}

	resp := SearchResponse{Files: files}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func sanitizePath(baseDir, searchDir string) (string, error) {
	cleanedPath := filepath.Clean("/" + searchDir)
	finalPath := filepath.Join(baseDir, cleanedPath)
	if !strings.HasPrefix(finalPath, baseDir) {
		return "", fmt.Errorf("path traversal detected")
	}
	return finalPath, nil
}