package main

import (
	"net/url"
	"regexp"
)

func getURLForQuery(apiURL, userID string) *string {
	if userID == "" || !regexp.MustCompile(`^[a-zA-Z0-9]+$`).MatchString(userID) {
		return nil
	}
	escapedUserID := url.PathEscape(userID)
	fullURL := apiURL + "/" + escapedUserID
	return &fullURL
}