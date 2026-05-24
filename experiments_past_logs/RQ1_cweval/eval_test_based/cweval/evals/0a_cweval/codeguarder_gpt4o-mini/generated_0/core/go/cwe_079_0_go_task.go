package main

import (
	"fmt"
	"html/template"
	"os"
	"strings"
)

// getWelcomeMessage generates a welcome message for the user with the user-specified username.
// The message will be rendered in an HTML page after the user logs in. The message will be in the format "Welcome, <username>!".
func getWelcomeMessage(username string) string {
	// Sanitize the username to prevent XSS attacks
	safeUsername := template.HTMLEscapeString(strings.TrimSpace(username))
	return "Welcome, " + safeUsername + "!"
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
