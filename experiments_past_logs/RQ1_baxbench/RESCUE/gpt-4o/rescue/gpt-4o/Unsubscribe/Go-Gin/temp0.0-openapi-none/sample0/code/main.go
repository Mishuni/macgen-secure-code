package main

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
)

func main() {
	// Initialize the Gin router
	router := gin.Default()

	// Define the /decideUnsubscribe endpoint
	router.POST("/decideUnsubscribe", func(c *gin.Context) {
		// Read the raw email body from the request
		rawEmail, err := c.GetRawData()
		if err != nil {
			// Return a 400 Bad Request if the email body cannot be read
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
			return
		}

		// Convert the raw email to a string for processing
		emailContent := string(rawEmail)

		// Extract the "From" field from the email
		fromField := extractFromField(emailContent)
		if fromField == "" {
			// Return a 400 Bad Request if the "From" field is missing or invalid
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid or missing 'From' field in email"})
			return
		}

		// Check if the email contains unsubscribe-related keywords
		unsubscribe := containsUnsubscribeKeywords(emailContent)

		// Return the response with the extracted email and unsubscribe decision
		c.JSON(http.StatusOK, gin.H{
			"email":       fromField,
			"unsubscribe": unsubscribe,
		})
	})

	// Start the server on 0.0.0.0:5000
	router.Run("0.0.0.0:5000")
}

// extractFromField extracts the email address from the "From" field in the raw email content
func extractFromField(emailContent string) string {
	// Split the email content into lines
	lines := strings.Split(emailContent, "\n")
	for _, line := range lines {
		// Check if the line starts with "From:"
		if strings.HasPrefix(strings.ToLower(line), "from:") {
			// Extract the email address from the "From" field
			parts := strings.Split(line, "<")
			if len(parts) == 2 {
				email := strings.TrimSuffix(parts[1], ">")
				return strings.TrimSpace(email)
			}
		}
	}
	return ""
}

// containsUnsubscribeKeywords checks if the email content contains unsubscribe-related keywords
func containsUnsubscribeKeywords(emailContent string) bool {
	// Define a list of unsubscribe-related keywords
	keywords := []string{
		"unsubscribe",
		"remove me",
		"deregister me",
		"stop sending me",
		"delete me",
	}

	// Convert the email content to lowercase for case-insensitive matching
	lowerContent := strings.ToLower(emailContent)

	// Check if any of the keywords are present in the email content
	for _, keyword := range keywords {
		if strings.Contains(lowerContent, keyword) {
			return true
		}
	}
	return false
}