package main

import (
	"fmt"
	"os"
)

func getWelcomeMessage(username string) string {
	return "Welcome, " + username + "!"
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
