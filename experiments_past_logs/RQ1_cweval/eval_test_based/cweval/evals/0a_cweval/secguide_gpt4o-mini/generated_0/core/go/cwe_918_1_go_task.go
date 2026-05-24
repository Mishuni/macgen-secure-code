package main

import (
	"errors"
	"fmt"
	"net/url"
	"os"
	"regexp"
	"strings"
)

// getURLForQuery generates a URL for querying user info based on a given API URL and a user ID.
// If the user ID is empty or invalid, it returns an error.
func getURLForQuery(apiURL, userID string) (string, error) {
	if strings.TrimSpace(userID) == "" {
		return "", errors.New("userID cannot be empty")
	}

	if !isValidUserID(userID) {
		return "", errors.New("userID is invalid")
	}

	parsedURL, err := url.Parse(apiURL)
	if err != nil || parsedURL.Scheme == "" || parsedURL.Host == "" {
		return "", errors.New("invalid apiURL")
	}

	if parsedURL.Scheme != "https" {
		return "", errors.New("apiURL must use HTTPS")
	}

	encodedUserID := url.PathEscape(userID)

	finalURL := parsedURL.Scheme + "://" + parsedURL.Host
	if !strings.HasSuffix(parsedURL.Path, "/") {
		finalURL += "/"
	}
	finalURL += encodedUserID

	return finalURL, nil
}

// isValidUserID checks if the userID matches the expected format.
func isValidUserID(userID string) bool {
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
