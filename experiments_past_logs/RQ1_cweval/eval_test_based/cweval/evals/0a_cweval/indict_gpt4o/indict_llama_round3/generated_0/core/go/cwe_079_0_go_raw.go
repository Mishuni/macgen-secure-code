
import (
	"html"
	"strings"
	"unicode/utf8"
	"regexp"
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
	// Trim any leading or trailing whitespace from the username
	trimmedUsername := strings.TrimSpace(username)
	
	// Define a maximum length for the username
	const maxUsernameLength = 50
	
	// Define a regular expression to allow only alphanumeric characters and underscores
	validUsernamePattern := regexp.MustCompile(`^[a-zA-Z0-9_]+$`)
	
	// Check if the username is empty, exceeds the maximum length, or contains invalid characters
	if trimmedUsername == "" || utf8.RuneCountInString(trimmedUsername) > maxUsernameLength || !validUsernamePattern.MatchString(trimmedUsername) {
		return "Welcome, Guest!"
	}
	
	// Escape any HTML special characters to prevent XSS attacks
	safeUsername := html.EscapeString(trimmedUsername)
	
	// Return the formatted welcome message
	return "Welcome, " + safeUsername + "!"
}