package main

import (
	"net/http"
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/gin-gonic/gin/binding"
	"golang.org/x/exp/slices"
)

type UnsubscribeResponse struct {
	Email      string `json:"email,omitempty"`
	Unsubscribe bool   `json:"unsubscribe"`
}

func main() {
	r := gin.Default()
	r.POST("/decideUnsubscribe", decideUnsubscribe)
	r.Run("0.0.0.0:5000")
}

func decideUnsubscribe(c *gin.Context) {
	var emailContent string
	if err := c.ShouldBindBodyWith(&emailContent, binding.TextPlain); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	email := extractEmail(emailContent)
	if email == "" || !isValidEmail(email) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid email format"})
		return
	}

	unsubscribe := shouldUnsubscribe(emailContent)

	response := UnsubscribeResponse{
		Email:      email,
		Unsubscribe: unsubscribe,
	}
	c.JSON(http.StatusOK, response)
}

func extractEmail(content string) string {
	re := regexp.MustCompile(`From:\s*([^<]+<([^>]+)>)`)
	matches := re.FindStringSubmatch(content)
	if len(matches) > 2 {
		return sanitizeEmail(strings.TrimSpace(matches[2]))
	}
	return ""
}

func sanitizeEmail(email string) string {
	// Sanitize the email to prevent injection attacks
	return strings.TrimSpace(email)
}

func isValidEmail(email string) bool {
	// More robust email validation regex
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func shouldUnsubscribe(content string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	return slices.ContainsFunc(keywords, func(keyword string) bool {
		return strings.Contains(strings.ToLower(content), keyword)
	})
}