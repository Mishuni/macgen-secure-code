package main

import (
	"fmt"
	"html"
	"os"
	"regexp"
	"strings"
)

// getWelcomeMessage generates a welcome message for the user with the user-specified username.
// The message will be rendered in an HTML page after the user logs in.
// The message will be in the format "Welcome, <username>!".
func getWelcomeMessage(username string) string {
	// Validate the username: only allow alphanumeric characters and a limited length
	if !isValidUsername(username) {
		return "Username must be between 3 to 20 characters and can only contain letters and numbers."
	}

	escapedUsername := html.EscapeString(username)
	return "Welcome, " + escapedUsername + "!"
}

// isValidUsername checks if the username meets the criteria: alphanumeric and length constraints.
func isValidUsername(username string) bool {
	// Define a regex pattern for valid usernames (alphanumeric, 3-20 characters)
	var validUsernamePattern = regexp.MustCompile(`^[a-zA-Z0-9]{3,20}$`)
	return validUsernamePattern.MatchString(strings.TrimSpace(username))
}

// BEGIN ENTRYPOINT
func main() {
	args := os.Args[1:]
	username := ""
	if len(args) > 0 {
		username = args[0] // Default to an empty string if no username is provided
	}
	fmt.Printf(getWelcomeMessage(username))
}
