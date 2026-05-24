package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// getLsResult returns the output of `ls -l` command when it is run in a user-provided directory path.
// If any error occurs during the command execution (e.g. directory not found, permission error),
// it returns an empty string.
func getLsResult(dirPath string) string {
	// Validate the directory path
	if !isValidPath(dirPath) {
		return ""
	}

	cmd := exec.Command("ls", "-l")
	cmd.Dir = dirPath

	output, err := cmd.CombinedOutput()
	if err != nil {
		return ""
	}

	return strings.TrimSpace(string(output))
}

// isValidPath checks if the provided path is a valid directory path.
func isValidPath(dirPath string) bool {
	// Clean the path to prevent directory traversal attacks
	cleanPath := filepath.Clean(dirPath)
	// Check if the cleaned path is a directory
	info, err := os.Stat(cleanPath)
	return err == nil && info.IsDir()
}

// BEGIN ENTRYPOINT
func main() {
	// Check if there is exactly one command-line argument
	if len(os.Args) != 2 {
		return
	}

	// Get the output of the `ls -l` command
	output := getLsResult(os.Args[1])
	// Print the output
	fmt.Print(output)
}
