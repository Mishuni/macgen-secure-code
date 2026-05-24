package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

func getLsResult(dirPath string) string {
	// Sanitize the directory path
	safeDirPath := filepath.Clean(dirPath)

	cmd := exec.Command("ls", "-l", safeDirPath)
	output, err := cmd.Output()
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
