package main

import (
	"encoding/json"
	"fmt"
	"io"
	"io/fs"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

const filesRoot = "./files"
const maxFileSize = 10 * 1024 * 1024 // 10 MB

type ErrorResponse struct {
	Error string `json:"error"`
}

type SuccessResponse struct {
	Files []string `json:"files"`
}

func main() {
	http.HandleFunc("/search", searchHandler)
	fmt.Println("Server starting on localhost:5000")
	http.ListenAndServe("localhost:5000", nil)
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	regexPattern := r.URL.Query().Get("regex")
	if regexPattern == "" {
		http.Error(w, "Missing regex parameter", http.StatusBadRequest)
		return
	}

	directory := r.URL.Query().Get("directory")
	if directory == "" {
		directory = "."
	}

	recursive := r.URL.Query().Get("recursive") == "true"

	// Validate directory path
	if err := validatePath(directory); err != nil {
		http.Error(w, "Invalid directory path", http.StatusBadRequest)
		return
	}

	// Compile regex safely
	regex, err := compileRegexSafely(regexPattern)
	if err != nil {
		http.Error(w, "Invalid or complex regex pattern", http.StatusBadRequest)
		return
	}

	// Search files
	matchingFiles, err := searchFiles(regex, directory, recursive)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	// Respond with matching files
	response := SuccessResponse{Files: matchingFiles}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func validatePath(path string) error {
	cleanPath := filepath.Clean(path)
	if strings.Contains(cleanPath, "..") {
		return fmt.Errorf("Invalid directory path")
	}
	absPath, err := filepath.Abs(filepath.Join(filesRoot, cleanPath))
	if err != nil {
		return fmt.Errorf("Invalid directory path")
	}
	if !strings.HasPrefix(absPath, filepath.Clean(filesRoot)) {
		return fmt.Errorf("Invalid directory path")
	}
	return nil
}

func compileRegexSafely(pattern string) (*regexp.Regexp, error) {
	// Use a simple regex compilation without timeout
	// Ensure the pattern is not too complex
	if len(pattern) > 1000 {
		return nil, fmt.Errorf("Regex pattern too complex")
	}
	return regexp.Compile(pattern)
}

func searchFiles(regex *regexp.Regexp, directory string, recursive bool) ([]string, error) {
	var matchingFiles []string
	rootPath := filepath.Join(filesRoot, directory)

	err := filepath.WalkDir(rootPath, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}

		// Skip directories if not recursive
		if d.IsDir() && !recursive && path != rootPath {
			return filepath.SkipDir
		}

		// Skip directories
		if d.IsDir() {
			return nil
		}

		// Open file
		file, err := os.Open(path)
		if err != nil {
			return err
		}
		defer file.Close()

		// Check file size
		fileInfo, err := file.Stat()
		if err != nil {
			return err
		}
		if fileInfo.Size() > maxFileSize {
			return nil
		}

		// Read file content in chunks
		buffer := make([]byte, 4096)
		for {
			n, err := file.Read(buffer)
			if err != nil && err != io.EOF {
				return err
			}
			if n == 0 {
				break
			}

			// Check if file content matches regex
			if regex.Match(buffer[:n]) {
				relativePath, err := filepath.Rel(filesRoot, path)
				if err != nil {
					return err
				}
				matchingFiles = append(matchingFiles, relativePath)
				break
			}
		}

		return nil
	})

	if err != nil {
		return nil, err
	}

	return matchingFiles, nil
}