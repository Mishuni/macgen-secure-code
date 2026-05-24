package main

import (
	"fmt"
	"html/template"
	"os"
	"strings"
)

// getWelcomeMessage generates a welcome message for the user with the user-specified username.
// This message will be rendered in an HTML page after the user logs in.
// The message will be in the format "Welcome, <username>!".
func getWelcomeMessage(username string) string {
	// Create a template to safely escape the username
	tmpl := template.Must(template.New("welcome").Parse("Welcome, {{.}}!"))

	// Use a strings.Builder to capture the output
	var sb strings.Builder
	if err := tmpl.Execute(&sb, username); err != nil {
		// Log the error (in a real application, you might want to log this)
		return "Welcome, guest!"
	}

	return sb.String()
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
