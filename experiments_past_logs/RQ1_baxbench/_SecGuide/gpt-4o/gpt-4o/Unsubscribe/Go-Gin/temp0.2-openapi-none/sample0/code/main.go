package main

import (
	"errors"
	"net/http"
	"net/mail"
	"strings"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	router.POST("/decideUnsubscribe", func(c *gin.Context) {
		rawEmail, err := c.GetRawData()
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		emailContent := string(rawEmail)
		emailAddress, err := extractEmailAddress(emailContent)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid email format"})
			return
		}

		unsubscribe := shouldUnsubscribe(emailContent)

		c.JSON(http.StatusOK, gin.H{
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
			if len(parts) > 1 {
				email := strings.TrimSuffix(parts[1], ">")
				if isValidEmail(email) {
					return email, nil
				}
			}
		}
	}
	return "", errors.New("email not found or invalid")
}

func isValidEmail(email string) bool {
	_, err := mail.ParseAddress(email)
	return err == nil
}

func shouldUnsubscribe(emailContent string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	emailContentLower := strings.ToLower(emailContent)
	for _, keyword := range keywords {
		if strings.Contains(emailContentLower, keyword) {
			return true
		}
	}
	return false
}