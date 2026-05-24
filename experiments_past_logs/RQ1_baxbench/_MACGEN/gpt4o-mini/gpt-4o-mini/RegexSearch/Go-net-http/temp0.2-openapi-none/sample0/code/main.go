package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

type SearchResponse struct {
	Files []string `json:"files"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

func isValidDirectory(directory string) bool {
	return regexp.MustCompile(`^[a-zA-Z0-9/_-]*$`).MatchString(directory)
}

func searchFiles(regexPattern, directory string, recursive bool) ([]string, error) {
	var matchingFiles []string
	err := filepath.Walk(filepath.Join("./files", directory), func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			content, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			if matched, _ := regexp.Match(regexPattern, content); matched {
				relativePath, _ := filepath.Rel("./files", path)
				matchingFiles = append(matchingFiles, relativePath)
			}
		}
		return nil
	})
	return matchingFiles, err
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

	if !isValidDirectory(directory) {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "Invalid directory"})
		return
	}

	if _, err := regexp.Compile(regex); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "Invalid regex pattern"})
		return
	}

	files, err := searchFiles(regex, directory, recursive)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(ErrorResponse{Error: "Error reading files"})
		return
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(SearchResponse{Files: files})
}

func main() {
	http.HandleFunc("/search", searchHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}