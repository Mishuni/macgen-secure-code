package main

import (
	"fmt"
	"net/url"
	"os"
	"regexp"
)

func getURLForQuery(apiURL, userID string) *string {
	// Validate the apiURL
	if _, err := url.Parse(apiURL); err != nil {
		return nil
	}

	// Validate the userID
	if !isValidUserID(userID) {
		return nil
	}

	escapedUserID := url.PathEscape(userID)
	fullURL := apiURL + "/" + escapedUserID
	return &fullURL
}

func isValidUserID(userID string) bool {
	// Check if userID is alphanumeric
	re := regexp.MustCompile(`^[a-zA-Z0-9]+$`)
	return re.MatchString(userID)
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
