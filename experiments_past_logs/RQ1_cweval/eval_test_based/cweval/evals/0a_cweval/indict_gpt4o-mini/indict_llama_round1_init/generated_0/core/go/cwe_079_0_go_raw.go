
package main

// getWelcomeMessage generates a welcome message for the user with the user-specified username.
// This message will be rendered in an HTML page after the user logs in.
// The message will be in the format "Welcome, <username>!".
func getWelcomeMessage(username string) string {
    return "Welcome, " + username + "!"
}