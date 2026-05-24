package main

import (
	"os"
	"path/filepath"
	"regexp"
)

func saveSecreteFile(directory string, filename string, content string) {
	if directory == "" || filename == "" || content == "" {
		return
	}

	// Clean the directory and filename to prevent path traversal
	directory = filepath.Clean(directory)
	filename = filepath.Clean(filename)

	// Validate filename using a strict allowlist (alphanumeric and some special characters)
	validFilename := regexp.MustCompile(`^[a-zA-Z0-9._-]+$`)
	if !validFilename.MatchString(filename) {
		return
	}

	// Ensure the directory exists and is writable
	dirInfo, err := os.Stat(directory)
	if err != nil || !dirInfo.IsDir() || dirInfo.Mode().Perm()&(1<<(uint(7))) == 0 {
		return
	}

	// Construct the full file path
	filePath := filepath.Join(directory, filename)

	// Create the file with restricted permissions
	file, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0600)
	if err != nil {
		return
	}
	defer file.Close()

	// Write the content to the file
	_, err = file.WriteString(content)
	if err != nil {
		return
	}

	// Set the file permissions to 0600
	err = os.Chmod(filePath, 0600)
	if err != nil {
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
