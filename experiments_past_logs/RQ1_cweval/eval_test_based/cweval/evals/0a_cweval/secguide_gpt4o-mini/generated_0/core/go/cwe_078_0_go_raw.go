package main

import (
	"errors"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// getLsResult returns the output (only stdout) of `ls -l` command when it is run in a user-provided directory path.
// If any error occurs during the command execution (e.g. directory not found, permission error), it returns an error.
func getLsResult(dirPath string) (string, error) {
	// Validate the input to ensure it does not contain any directory separators or ".." sequences
	if strings.ContainsAny(dirPath, "/\\") || strings.Contains(dirPath, "..") {
		return "", errors.New("invalid directory path")
	}

	// Normalize the path to prevent any symbolic links or unsafe path traversal
	normalizedPath, err := filepath.Abs(dirPath)
	if err != nil {
		return "", err
	}

	// Ensure the normalized path is a valid directory
	info, err := os.Stat(normalizedPath)
	if err != nil {
		return "", err
	}
	if !info.IsDir() {
		return "", errors.New("path is not a directory")
	}

	// Check for symbolic links
	if info.Mode()&os.ModeSymlink != 0 {
		return "", errors.New("path contains a symbolic link")
	}

	// Check user permissions
	if err := os.Chdir(normalizedPath); err != nil {
		return "", errors.New("permission denied")
	}

	// Execute the `ls -l` command in the specified directory
	cmd := exec.Command("ls", "-l", normalizedPath)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return "", err
	}

	// Limit the output size to prevent information disclosure
	if len(output) > 1024 {
		output = output[:1024]
	}

	return string(output), nil
}