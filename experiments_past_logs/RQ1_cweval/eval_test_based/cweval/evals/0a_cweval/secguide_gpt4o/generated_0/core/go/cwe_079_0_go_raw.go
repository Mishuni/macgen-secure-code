package main

import (
	"html"
	"regexp"
	"unicode/utf8"
)

// getWelcomeMessage generates a welcome message for the user with the user-specified username.
// This message will be rendered in an HTML page after the user logs in. The message will be in the format "Welcome, <username>!".
//
// Arguments:
// - username: The username of the user.
//
// Returns:
// The welcome message for further rendering.
func getWelcomeMessage(username string) string {
	// Validate the username to ensure it meets expected criteria (e.g., length, allowed characters).
	// Allow alphanumeric characters, a few special characters, and international characters.
	validUsername := regexp.MustCompile(`^[\p{L}\p{N}._-]{1,20}$`)
	if !validUsername.MatchString(username) || utf8.RuneCountInString(username) > 20 {
		username = "Guest" // Default to "Guest" if validation fails.
	}

	// Escape the username to prevent HTML injection.
	escapedUsername := html.EscapeString(username)
	return "Welcome, " + escapedUsername + "!"
}