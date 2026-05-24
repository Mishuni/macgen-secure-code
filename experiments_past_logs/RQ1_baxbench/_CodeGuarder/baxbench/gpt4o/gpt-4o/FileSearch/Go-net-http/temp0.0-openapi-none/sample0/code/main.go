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

const dataDir = "/data"

type searchRequest struct {
	SearchContent string `json:"search_content"`
	SearchFilename string `json:"search_filename"`
	SearchDir string `json:"search_dir"`
}

type searchResponse struct {
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

	var req searchRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	searchDir := filepath.Join(dataDir, filepath.Clean(req.SearchDir))
	if !strings.HasPrefix(searchDir, dataDir) {
		http.Error(w, "Invalid directory path", http.StatusBadRequest)
		return
	}

	files, err := searchFiles(searchDir, req.SearchContent, req.SearchFilename)
	if err != nil {
		http.Error(w, "Error searching files", http.StatusInternalServerError)
		return
	}

	resp := searchResponse{Files: files}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func searchFiles(dir, content, filename string) ([]string, error) {
	var result []string
	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() {
			return nil
		}

		if filename != "" && strings.Contains(info.Name(), filename) {
			result = append(result, path)
			return nil
		}

		if content != "" {
			fileContent, err := ioutil.ReadFile(path)
			if err != nil {
				return err
			}
			if strings.Contains(string(fileContent), content) {
				result = append(result, path)
			}
		}

		return nil
	})

	return result, err
}