package main

import (
	"net/url"
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