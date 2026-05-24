package main

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	router.POST("/decideUnsubscribe", func(c *gin.Context) {
		rawEmail, err := c.GetRawData()
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
			return
		}

		emailContent := string(rawEmail)
		emailAddress, err := extractEmailAddress(emailContent)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid email format"})
			return
		}

		unsubscribe := determineUnsubscribeDecision(emailContent)

		c.JSON(http.StatusOK, gin.H{
			"email":       emailAddress,
			"unsubscribe": unsubscribe,
		})
	})

	router.Run("0.0.0.0:5000")
}

func extractEmailAddress(emailContent string) (string, error) {
	lines := strings.Split(emailContent, "\n")
	for _, line := range lines {
		if strings.HasPrefix(line, "From:") {
			parts := strings.Split(line, "<")
			if len(parts) == 2 {
				email := strings.TrimSuffix(parts[1], ">")
				return email, nil
			}
		}
	}
	return "", http.ErrNoLocation
}

func determineUnsubscribeDecision(emailContent string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	emailContentLower := strings.ToLower(emailContent)
	for _, keyword := range keywords {
		if strings.Contains(emailContentLower, keyword) {
			return true
		}
	}
	return false
}