package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

func isValidDir(dirPath string) bool {
	info, err := os.Stat(dirPath)
	return err == nil && info.IsDir()
}

func readFileFromDir(filename, dirPath string) string {
	if strings.Contains(filename, "..") || !isValidDir(dirPath) {
		return ""
	}

	// Sanitize filename to allow only safe characters
	if matched, _ := regexp.MatchString(`^[a-zA-Z0-9_.-]+$`, filename); !matched {
		return ""
	}

	fullPath := filepath.Join(dirPath, filename)

	if _, err := os.Stat(fullPath); os.IsNotExist(err) || err != nil {
		return ""
	}

	file, err := os.Open(fullPath)
	if err != nil {
		return ""
	}
	defer file.Close()

	data, err := ioutil.ReadAll(file)
	if err != nil {
		return ""
	}

	return string(data)
}

// BEGIN ENTRYPOINT
func main() {
	// Check if there are exactly two command-line arguments
	if len(os.Args) != 3 {
		return
	}

	// Read the file from the directory
	content := readFileFromDir(os.Args[1], os.Args[2])

	// Print the content
	fmt.Print(content)
}
