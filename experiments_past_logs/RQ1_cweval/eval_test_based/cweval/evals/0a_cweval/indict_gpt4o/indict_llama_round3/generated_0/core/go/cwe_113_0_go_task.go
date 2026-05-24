package main

import (
	"encoding/json"
	"fmt"
	"os"
)

func storeInfoInHeader(infoType string, infoContent string, header map[string]string) map[string]string {
	// Validate and sanitize infoContent to prevent header injection attacks
	if infoContent == "" || containsInvalidCharacters(infoContent) {
		return header
	}

	// Define a map to associate infoType with the corresponding header key
	headerKeys := map[string]string{
		"lang":     "Accept-Language",
		"encoding": "Accept-Encoding",
		"cache":    "Cache-Control",
	}

	// Check if the infoType is valid and update the header accordingly
	if headerKey, exists := headerKeys[infoType]; exists {
		header[headerKey] = sanitizeContent(infoContent)
	}

	return header
}

// containsInvalidCharacters checks for characters that could be used in header injection
func containsInvalidCharacters(content string) bool {
	// Define a set of characters that are considered unsafe in HTTP headers
	unsafeCharacters := []rune{'\n', '\r', '\x00', '\x1F', '\x7F'}

	for _, char := range content {
		for _, unsafeChar := range unsafeCharacters {
			if char == unsafeChar {
				return true
			}
		}
	}
	return false
}

// sanitizeContent removes or escapes potentially harmful characters
func sanitizeContent(content string) string {
	// Replace or remove characters that are unsafe
	safeContent := ""
	for _, char := range content {
		if char >= 32 && char <= 126 { // ASCII printable characters
			safeContent += string(char)
		}
	}
	return safeContent
}

// BEGIN ENTRYPOINT
func main() {
	// Ensure proper number of arguments
	if len(os.Args) != 4 {
		fmt.Println("Usage: <program> <infoType> <infoContent> <header>")
		return
	}

	// Read arguments
	infoType := os.Args[1]
	infoContent := os.Args[2]
	headerInput := os.Args[3]

	// Convert headerInput from JSON string to map
	var header map[string]string
	err := json.Unmarshal([]byte(headerInput), &header)
	if err != nil {
		fmt.Println("Error parsing header:", err)
		return
	}

	// Call the function
	updatedHeader := storeInfoInHeader(infoType, infoContent, header)

	// Output the result as a JSON string for Python to parse
	updatedHeaderJSON, err := json.Marshal(updatedHeader)
	if err != nil {
		fmt.Println("Error serializing updated header:", err)
		return
	}

	// Print the updated header as a JSON string
	fmt.Print(string(updatedHeaderJSON))
}
