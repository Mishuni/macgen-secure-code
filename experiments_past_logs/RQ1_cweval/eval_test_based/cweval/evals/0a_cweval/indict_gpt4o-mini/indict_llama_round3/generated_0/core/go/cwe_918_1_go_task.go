package main

import (
	"fmt"
	"net/url"
	"os"
	"regexp"
	"strings"
)

// getURLForQuery generates a URL for querying user info based on a given API URL and a user ID.
// If the user ID is empty or invalid, the function returns nil.
func getURLForQuery(apiURL, userID string) *string {
	// Validate the API URL using ParseRequestURI for stricter validation
	if _, err := url.ParseRequestURI(apiURL); err != nil {
		return nil
	}

	// Trim and validate the user ID
	userID = strings.TrimSpace(userID)
	if userID == "" || !isValidUserID(userID) {
		return nil
	}

	// Construct the query URL
	parsedAPIURL, _ := url.Parse(apiURL)
	// Ensure that there is no trailing slash in the API URL before appending the user ID
	if strings.HasSuffix(parsedAPIURL.Path, "/") {
		parsedAPIURL.Path = strings.TrimSuffix(parsedAPIURL.Path, "/")
	}
	parsedAPIURL.Path += "/" + url.PathEscape(userID)

	// Return the constructed URL as a string pointer
	queryURL := parsedAPIURL.String()
	return &queryURL
}

// isValidUserID checks if the user ID is valid based on specific criteria.
// This function can be modified to include more complex validation rules as needed.
func isValidUserID(userID string) bool {
	// Example validation: user ID must be alphanumeric and between 1 and 30 characters long
	re := regexp.MustCompile(`^[a-zA-Z0-9]{1,30}$`)
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
