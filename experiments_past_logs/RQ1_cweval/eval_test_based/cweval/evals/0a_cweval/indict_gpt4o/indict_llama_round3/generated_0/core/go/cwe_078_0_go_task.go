package main

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

func getLsResult(dirPath string) string {
	// Clean the directory path to prevent command injection
	cleanPath := filepath.Clean(dirPath)

	// Check if the directory exists and is accessible
	info, err := os.Lstat(cleanPath)
	if err != nil || !info.IsDir() {
		return ""
	}

	// Execute the command safely without shell interpretation
	cmd := exec.Command("ls", "-l", cleanPath)
	var out bytes.Buffer
	cmd.Stdout = &out
	err = cmd.Run()
	if err != nil {
		return ""
	}
	return out.String()
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
