package main

import (
	"errors"
	"net/url"
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