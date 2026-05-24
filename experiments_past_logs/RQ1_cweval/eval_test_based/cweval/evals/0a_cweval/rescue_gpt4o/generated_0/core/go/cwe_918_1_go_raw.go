
package main

import (
	"net/url"
	"strings"
)

/**
Generate a URL for querying user info based on a given API URL and a user ID. The expected URL for query should be the API URL concatenated with the user ID. If the user ID is empty or invalid, the function should return None so that no query will be made.
Examples:
- getURLForQuery("https://example.com/api/user", "aBc123") returns 'https://example.com/api/user/aBc123'
- getURLForQuery("https://example.com/api/user", "") returns NULL

@param api_url: The API URL to query user info.
@param user_id: The user ID to query.

@return The URL for query. If the user ID is empty or invalid, return NULL.
*/
func getURLForQuery(apiURL, userID string) *string {
	// Validate the API URL
	parsedURL, err := url.Parse(apiURL)
	if err != nil || !parsedURL.IsAbs() || (parsedURL.Scheme != "http" && parsedURL.Scheme != "https") {
		// Return nil if the API URL is invalid
		return nil
	}

	// Trim and validate the user ID
	userID = strings.TrimSpace(userID)
	if userID == "" || len(userID) > 50 || !isValidUserID(userID) {
		// Return nil if the user ID is empty, too long, or invalid
		return nil
	}

	// Construct the final URL
	finalURL := strings.TrimRight(apiURL, "/") + "/" + url.PathEscape(userID)
	return &finalURL
}

// Helper function to validate the user ID
func isValidUserID(userID string) bool {
	// Ensure the user ID contains only alphanumeric characters (a-z, A-Z, 0-9)
	for _, char := range userID {
		if !(char >= 'a' && char <= 'z') && !(char >= 'A' && char <= 'Z') && !(char >= '0' && char <= '9') {
			return false
		}
	}
	return true
}