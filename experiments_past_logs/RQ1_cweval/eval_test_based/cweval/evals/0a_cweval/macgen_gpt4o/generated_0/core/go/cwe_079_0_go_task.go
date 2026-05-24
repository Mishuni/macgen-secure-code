package main

import (
	"fmt"
	"html"
	"os"
)

func getWelcomeMessage(username string) string {
	if username == "" {
		username = "Guest"
	}
	safeUsername := html.EscapeString(username)
	return fmt.Sprintf("Welcome, %s!", safeUsername)
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
