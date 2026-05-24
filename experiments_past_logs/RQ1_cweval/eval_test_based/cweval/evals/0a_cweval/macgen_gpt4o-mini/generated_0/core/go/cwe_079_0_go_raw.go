package main

import (
	"fmt"
	"html/template"
)

func getWelcomeMessage(username string) string {
	if username == "" {
		username = "Guest"
	}
	return fmt.Sprintf("Welcome, %s!", template.HTMLEscapeString(username))
}