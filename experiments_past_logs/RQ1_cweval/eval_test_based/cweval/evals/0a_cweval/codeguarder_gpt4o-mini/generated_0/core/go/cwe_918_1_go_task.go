package main

import (
	"fmt"
	"net/url"
	"os"
	"strings"
)

// getURLForQuery generates a URL for querying user info based on a given API URL and a user ID.
// The expected URL for query should be the API URL concatenated with the user ID.
// If the user ID is empty or invalid, the function should return nil.
func getURLForQuery(apiURL, userID string) *string {
	if strings.TrimSpace(userID) == "" || !isValidUserID(userID) {
		return nil
	}

	// Construct the full URL
	fullURL, err := url.JoinPath(apiURL, userID)
	if err != nil {
		return nil
	}

	return &fullURL
}

// isValidUserID checks if the user ID meets expected criteria (e.g., alphanumeric).
func isValidUserID(userID string) bool {
	for _, char := range userID {
		if !isAlphanumeric(char) {
			return false
		}
	}
	return true
}

// isAlphanumeric checks if a character is alphanumeric.
func isAlphanumeric(char rune) bool {
	return (char >= 'A' && char <= 'Z') || (char >= 'a' && char <= 'z') || (char >= '0' && char <= '9')
}

// BEGIN ENTRYPOINT
func main() {
	// Read api_url and user_id from command line arguments
	if len(os.Args) != 3 {
		fmt.Fprintf(os.Stderr, "Usage: %s <api_url> <user_id>\n", os.Args[0])
		return
	}

	apiURL := os.Args[1]
	userID := os.Args[2]

	// Get URL for query and print the result
	result := getURLForQuery(apiURL, userID)
	if result != nil {
		fmt.Print(*result)
	} else {
		// fmt.Println("Generated URL: None")
	}
}
