package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
)

type SearchResponse struct {
	Files []string `json:"files"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

func searchFiles(regexPattern, directory string, recursive bool) ([]string, error) {
	var files []string
	err := filepath.Walk(filepath.Join("./files", directory), func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			content, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			matched, err := regexp.Match(regexPattern, content)
			if err != nil {
				return err
			}
			if matched {
				relPath, _ := filepath.Rel("./files", path)
				files = append(files, relPath)
			}
		}
		if !recursive && info.IsDir() {
			return filepath.SkipDir
		}
		return nil
	})

	if err != nil {
		return nil, err
	}
	return files, nil
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	regex := r.URL.Query().Get("regex")
	directory := r.URL.Query().Get("directory")
	recursive := r.URL.Query().Get("recursive") == "true"

	if regex == "" {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "Missing required parameter: regex"})
		return
	}

	if _, err := regexp.Compile(regex); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "Invalid regex pattern"})
		return
	}

	if directory == "" {
		directory = "."
	}

	files, err := searchFiles(regex, directory, recursive)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(ErrorResponse{Error: err.Error()})
		return
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(SearchResponse{Files: files})
}

func main() {
	http.HandleFunc("/search", searchHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}