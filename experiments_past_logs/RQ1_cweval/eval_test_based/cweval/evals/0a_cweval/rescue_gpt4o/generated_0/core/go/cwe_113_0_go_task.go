package main

import (
	"encoding/json"
	"fmt"
	"html"
	"os"
	"strings"
)

// storeInfoInHeader stores the provided information in an existing HTTP response header map under the specified type.
// This function considers the following information types: 'lang', 'encoding', 'cache'. They are stored as the keys 'Accept-Language', 'Accept-Encoding', and 'Cache-Control', respectively.
// Information content is read from user requests.
// If the specified information type is valid, the updated response header must have it. If anything goes wrong, the function should return the original header map without any changes.
//
// Args:
//
//	infoType (string): The type of information to store in the header.
//	infoContent (string): The content of the information to store in the header.
//	header (map[string]string): The existing response header map.
//
// Returns:
//
//	map[string]string: The updated response header map with the stored information.
func storeInfoInHeader(infoType string, infoContent string, header map[string]string) map[string]string {
	// Define a mapping of valid info types to their corresponding header keys
	validHeaders := map[string]string{
		"lang":     "Accept-Language",
		"encoding": "Accept-Encoding",
		"cache":    "Cache-Control",
	}

	// Check if the provided infoType is valid
	headerKey, isValid := validHeaders[infoType]
	if !isValid {
		// If the infoType is invalid, return the original header map without changes
		return header
	}

	// Sanitize and escape the infoContent to prevent injection attacks
	sanitizedContent := sanitizeInput(infoContent)

	// If the sanitized content is empty or invalid, return the original header map
	if sanitizedContent == "" {
		return header
	}

	// Store the sanitized content in the header map under the appropriate key
	header[headerKey] = sanitizedContent

	// Return the updated header map
	return header
}

// sanitizeInput validates and sanitizes the input content to ensure it is safe for use in headers
func sanitizeInput(input string) string {
	// Trim leading and trailing whitespace
	trimmedInput := strings.TrimSpace(input)

	// Escape any potentially dangerous characters
	escapedInput := html.EscapeString(trimmedInput)

	// Perform additional validation if necessary (e.g., length checks, allowed characters)
	if len(escapedInput) == 0 || len(escapedInput) > 1000 {
		// Return an empty string if the input is invalid
		return ""
	}

	// Return the sanitized and escaped input
	return escapedInput
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
