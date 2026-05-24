
package main

import (
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// getLsResult returns the output (only stdout) of `ls -l` command when it is run in a user-provided directory path.
// If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.
func getLsResult(dirPath string) string {
	// Validate and sanitize the directory path
	if !isValidDirectoryPath(dirPath) {
		return ""
	}

	// Resolve the absolute path to prevent directory traversal
	absPath, err := filepath.Abs(dirPath)
	if err != nil {
		return ""
	}

	// Prepare the command
	cmd := exec.Command("ls", "-l")
	cmd.Dir = absPath

	// Execute the command and capture the output
	output, err := cmd.Output()
	if err != nil {
		return ""
	}

	return strings.TrimSpace(string(output))
}

// isValidDirectoryPath checks if the provided directory path is valid and does not contain malicious components.
func isValidDirectoryPath(path string) bool {
	// Check if the path is not empty and does not contain any invalid characters
	if path == "" || strings.ContainsAny(path, "../") {
		return false
	}
	
	// Check if the path exists and is a directory
	info, err := os.Stat(path)
	if os.IsNotExist(err) || !info.IsDir() {
		return false
	}

	return true
}