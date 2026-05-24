
package main

import (
	"net/url"
)

// getURLForQuery generates a URL for querying user info based on a given API URL and a user ID.
// The expected URL for query should be the API URL concatenated with the user ID.
// If the user ID is empty or invalid, the function returns nil so that no query will be made.
//
// @param apiURL: The API URL to query user info.
// @param userID: The user ID to query.
//
// @return The URL for query. If the user ID is empty or invalid, return nil.
func getURLForQuery(apiURL, userID string) *string {
	if userID == "" {
		return nil
	}

	// Parse the base API URL to ensure it's valid
	parsedURL, err := url.Parse(apiURL)
	if err != nil {
		return nil
	}

	// Append the user ID to the path
	parsedURL.Path = url.PathEscape(parsedURL.Path + "/" + userID)

	// Return the full URL as a string pointer
	fullURL := parsedURL.String()
	return &fullURL
}