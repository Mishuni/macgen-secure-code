
package main

import (
	"io/ioutil"
	"os"
	"path/filepath"
)

func readFileFromDir(filename, dirPath string) string {
	// Clean the directory path to prevent path traversal
	cleanDirPath, err := filepath.Abs(dirPath)
	if err != nil {
		return ""
	}

	// Clean the filename to prevent path traversal
	cleanFilename := filepath.Clean(filename)
	if cleanFilename != filename || filepath.IsAbs(cleanFilename) {
		return ""
	}

	// Join the cleaned directory path and filename
	filePath := filepath.Join(cleanDirPath, cleanFilename)

	// Check if the file path is within the intended directory
	if !isSubPath(cleanDirPath, filePath) {
		return ""
	}

	// Read the file content
	content, err := ioutil.ReadFile(filePath)
	if err != nil {
		return ""
	}
	return string(content)
}

// Helper function to check if a path is a subpath of a given directory
func isSubPath(basePath, targetPath string) bool {
	rel, err := filepath.Rel(basePath, targetPath)
	if err != nil {
		return false
	}
	return !filepath.IsAbs(rel) && !relHasParentDir(rel)
}

// Helper function to check if a relative path contains parent directory references
func relHasParentDir(relPath string) bool {
	return relPath == ".." || filepath.HasPrefix(relPath, ".."+string(os.PathSeparator))
}