
package main

import (
	"strings"
)

// getURLForQuery generates a URL for querying user info based on a given API URL and a user ID.
// If the user ID is empty or invalid, the function returns nil.
func getURLForQuery(apiURL, userID string) *string {
	if strings.TrimSpace(userID) == "" {
		return nil
	}
	queryURL := apiURL + "/" + userID
	return &queryURL
}