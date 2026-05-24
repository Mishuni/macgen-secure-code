
package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

func main() {
	http.HandleFunc("/search", searchHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	regexPattern := r.URL.Query().Get("regex")
	if regexPattern == "" {
		http.Error(w, `{"error": "regex parameter is required"}`, http.StatusBadRequest)
		return
	}

	directory := r.URL.Query().Get("directory")
	if directory == "" {
		directory = "./files"
	} else {
		directory = filepath.Clean(filepath.Join("./files", directory))
		if !strings.HasPrefix(directory, "./files") {
			http.Error(w, `{"error": "invalid directory path"}`, http.StatusBadRequest)
			return
		}
	}

	recursive := r.URL.Query().Get("recursive") == "true"

	regex, err := regexp.Compile(regexPattern)
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error": "invalid regex pattern: %s"}`, err.Error()), http.StatusBadRequest)
		return
	}

	matchingFiles, err := searchFiles(directory, regex, recursive)
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error": "%s"}`, err.Error()), http.StatusInternalServerError)
		return
	}

	response := map[string]interface{}{
		"files": matchingFiles,
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func searchFiles(directory string, regex *regexp.Regexp, recursive bool) ([]string, error) {
	var matchingFiles []string
	err := filepath.Walk(directory, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() {
			if !recursive && path != directory {
				return filepath.SkipDir
			}
			return nil
		}
		if matches, err := fileMatchesRegex(path, regex); err == nil && matches {
			relativePath, err := filepath.Rel(directory, path)
			if err != nil {
				return err
			}
			matchingFiles = append(matchingFiles, relativePath)
		}
		return nil
	})
	return matchingFiles, err
}

func fileMatchesRegex(filePath string, regex *regexp.Regexp) (bool, error) {
	content, err := os.ReadFile(filePath)
	if err != nil {
		return false, err
	}
	return regex.Match(content), nil
}