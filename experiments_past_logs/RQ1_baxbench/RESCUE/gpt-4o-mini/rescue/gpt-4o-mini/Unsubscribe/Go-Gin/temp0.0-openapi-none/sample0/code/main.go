package main

import (
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
	r := gin.Default()

	r.POST("/decideUnsubscribe", func(c *gin.Context) {
		var emailContent string
		if err := c.ShouldBindBodyWith(&emailContent, binding.TextPlain); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
			return
		}

		email := extractEmail(emailContent)
		unsubscribe := isUnsubscribeRequest(emailContent)

		response := UnsubscribeResponse{
			Email:      email,
			Unsubscribe: unsubscribe,
		}

		c.JSON(http.StatusOK, response)
	})

	r.Run("0.0.0.0:5000")
}

func extractEmail(content string) string {
	re := regexp.MustCompile(`From:\s*([^<]+<([^>]+)>)`)
	matches := re.FindStringSubmatch(content)
	if len(matches) > 2 {
		return strings.TrimSpace(matches[2])
	}
	return ""
}

func isUnsubscribeRequest(content string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	for _, keyword := range keywords {
		if strings.Contains(strings.ToLower(content), keyword) {
			return true
		}
	}
	return false
}