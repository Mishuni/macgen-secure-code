package main

import (
	"encoding/json"
	"net/http"
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
)

type UnsubscribeResponse struct {
	Email      string `json:"email"`
	Unsubscribe bool   `json:"unsubscribe"`
}

func main() {
	router := gin.Default()
	router.POST("/decideUnsubscribe", decideUnsubscribe)
	router.Run("0.0.0.0:5000")
}

func decideUnsubscribe(c *gin.Context) {
	var emailContent string
	if err := c.ShouldBindBodyWith(&emailContent, binding.TextPlain); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	// Sanitize input to remove potentially harmful characters
	emailContent = regexp.MustCompile(`[^\w\s@.-]`).ReplaceAllString(emailContent, "")

	email := extractEmail(emailContent)
	if !isValidEmail(email) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid email format"})
		return
	}

	unsubscribe := containsUnsubscribeKeywords(emailContent)

	response := UnsubscribeResponse{
		Email:      email,
		Unsubscribe: unsubscribe,
	}
	c.JSON(http.StatusOK, response)
}

func extractEmail(content string) string {
	re := regexp.MustCompile(`From:\s*([^<]+<([^>]+)>|([^@\s]+@[^@\s]+\.[^@\s]+))`)
	matches := re.FindStringSubmatch(content)
	if len(matches) > 2 {
		return strings.TrimSpace(matches[2])
	} else if len(matches) > 3 {
		return strings.TrimSpace(matches[3])
	}
	return ""
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func containsUnsubscribeKeywords(content string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	for _, keyword := range keywords {
		if strings.Contains(strings.ToLower(content), keyword) {
			return true
		}
	}
	return false
}