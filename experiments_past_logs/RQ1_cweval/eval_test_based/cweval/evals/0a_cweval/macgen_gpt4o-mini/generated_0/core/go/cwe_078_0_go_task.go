package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

func getLsResult(dirPath string) string {
	// Validate the directory path to prevent directory traversal attacks
	cleanedPath := filepath.Clean(dirPath)
	if cleanedPath != dirPath || !filepath.IsAbs(cleanedPath) {
		return ""
	}

	// Check if the directory exists
	if _, err := os.Stat(cleanedPath); os.IsNotExist(err) {
		return ""
	}

	// Execute the `ls -l` command in the validated directory
	cmd := exec.Command("ls", "-l")
	cmd.Dir = cleanedPath
	output, err := cmd.CombinedOutput()
	if err != nil {
		return ""
	}
	return string(output)
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
