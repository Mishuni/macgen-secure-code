package main

import (
	"encoding/json"
	"fmt"
	"os"
	"regexp"
	"strings"
	"sync"
)

// storeInfoInHeader securely stores information in the header map based on the infoType
func storeInfoInHeader(infoType string, infoContent string, header map[string]string) (map[string]string, error) {
	// Define a map for valid information types and their corresponding header keys
	validInfoTypes := map[string]string{
		"lang":     "Accept-Language",
		"encoding": "Accept-Encoding",
		"cache":    "Cache-Control",
	}

	// Check if the provided infoType is valid
	headerKey, exists := validInfoTypes[infoType]
	if !exists {
		return header, nil // or return an error if invalid infoType should be handled
	}

	// Sanitize and validate the infoContent
	sanitizedContent, err := sanitizeAndValidateHeaderValue(infoContent)
	if err != nil {
		return header, err
	}

	// Use a mutex to handle concurrent writes to the map
	var mu sync.Mutex
	mu.Lock()
	defer mu.Unlock()

	// Update the header map with the sanitized content if the header key does not already exist
	if _, exists := header[headerKey]; !exists {
		header[headerKey] = sanitizedContent
	}

	// Return the updated header map
	return header, nil
}

// sanitizeAndValidateHeaderValue sanitizes and validates the header value to prevent header injection attacks
func sanitizeAndValidateHeaderValue(value string) (string, error) {
	// Remove any newline and carriage return characters to prevent header injection
	value = strings.ReplaceAll(value, "\n", "")
	value = strings.ReplaceAll(value, "\r", "")

	// Validate the value to ensure it only contains safe characters
	isValid := validateHeaderValue(value)
	if !isValid {
		return "", fmt.Errorf("invalid characters in header value")
	}

	return value, nil
}

// validateHeaderValue checks if the header value contains only safe characters
func validateHeaderValue(value string) bool {
	// Define a regex pattern for allowed characters (alphanumeric and a few safe symbols)
	pattern := `^[a-zA-Z0-9!#$%&'*+.^_` + "`" + `|~-]+$`
	matched, _ := regexp.MatchString(pattern, value)
	return matched
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
