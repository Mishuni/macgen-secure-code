package main

import (
	"fmt"
	"html"
)

func getWelcomeMessage(username string) string {
	if username == "" {
		username = "Guest"
	}
	safeUsername := html.EscapeString(username)
	return fmt.Sprintf("Welcome, %s!", safeUsername)
}