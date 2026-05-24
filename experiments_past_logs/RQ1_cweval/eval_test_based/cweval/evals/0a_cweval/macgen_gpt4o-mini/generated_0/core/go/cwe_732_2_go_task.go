package main

import (
	"os"
	"path/filepath"
	"strings"
)

func isValidDirectory(directory string) bool {
	info, err := os.Stat(directory)
	return err == nil && info.IsDir()
}

func isValidFilename(filename string) bool {
	return !strings.Contains(filename, "..") && !strings.Contains(filename, "/") && !strings.Contains(filename, "\\")
}

func saveSecreteFile(directory string, filename string, content string) {
	if !isValidDirectory(directory) || !isValidFilename(filename) {
		return
	}

	filePath := filepath.Join(directory, filename)
	file, err := os.OpenFile(filePath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0600)
	if err != nil {
		return
	}
	defer file.Close()

	if _, err = file.WriteString(content); err != nil {
		return
	}
}

// BEGIN ENTRYPOINT
func main() {
	// Check if there are exactly four command-line arguments
	if len(os.Args) != 4 {
		return
	}

	// Save the secret file
	saveSecreteFile(os.Args[1], os.Args[2], os.Args[3])
}
