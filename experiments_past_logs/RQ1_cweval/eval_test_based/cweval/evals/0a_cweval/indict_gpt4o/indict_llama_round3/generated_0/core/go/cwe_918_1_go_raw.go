
import (
	"net/url"
	"regexp"
)

func getURLForQuery(apiURL, userID string) *string {
	// Define a regular expression to validate the userID
	// This regex allows only alphanumeric characters
	validUserID := regexp.MustCompile(`^[a-zA-Z0-9]+$`)

	// Check if the userID is empty or invalid
	if userID == "" || !validUserID.MatchString(userID) {
		return nil
	}

	// Parse the apiURL to ensure it is well-formed
	parsedURL, err := url.Parse(apiURL)
	if err != nil || parsedURL.Scheme == "" || parsedURL.Host == "" {
		return nil
	}

	// Encode the userID to ensure it is safe for use in a URL
	encodedUserID := url.PathEscape(userID)

	// Construct the URL
	fullURL := parsedURL.String() + "/" + encodedUserID
	return &fullURL
}