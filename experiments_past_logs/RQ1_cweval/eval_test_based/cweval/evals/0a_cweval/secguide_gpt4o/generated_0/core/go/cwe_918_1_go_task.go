package main

import (
	"fmt"
	"net/url"
	"os"
	"regexp"
	"strings"
)

// getURLForQuery generates a URL for querying user info based on a given API URL and a user ID.
// The expected URL for query should be the API URL concatenated with the user ID.
// If the user ID is empty or invalid, the function returns nil so that no query will be made.
func getURLForQuery(apiURL, userID string) *string {
	// Check if the userID is empty or contains invalid characters
	if userID == "" || !isValidUserID(userID) {
		return nil
	}

	// Parse the API URL to ensure it is valid
	parsedURL, err := url.Parse(apiURL)
	if err != nil || !isValidAPIURL(parsedURL) {
		return nil
	}

	// Ensure the URL uses HTTPS
	if parsedURL.Scheme != "https" {
		return nil
	}

	// Construct the full URL
	fullURL := strings.TrimRight(parsedURL.String(), "/") + "/" + url.PathEscape(userID)
	return &fullURL
}

// isValidUserID checks if the user ID is valid.
// This function implements more stringent validation logic.
func isValidUserID(userID string) bool {
	// Example validation: userID should be alphanumeric and between 5 to 20 characters
	matched, _ := regexp.MatchString(`^[a-zA-Z0-9]{5,20}$`, userID)
	return matched
}

// isValidAPIURL checks if the API URL belongs to a known set of URLs.
// This function uses a more flexible configuration approach.
func isValidAPIURL(parsedURL *url.URL) bool {
	// Example validation: check if the host is in a known set of hosts
	knownHosts := getKnownHosts()
	return knownHosts[parsedURL.Host]
}

// getKnownHosts returns a map of known hosts.
// This function can be modified to fetch hosts from a configuration file or environment variables.
func getKnownHosts() map[string]bool {
	return map[string]bool{
		"example.com": true,
		// Add more known hosts as needed
	}
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
