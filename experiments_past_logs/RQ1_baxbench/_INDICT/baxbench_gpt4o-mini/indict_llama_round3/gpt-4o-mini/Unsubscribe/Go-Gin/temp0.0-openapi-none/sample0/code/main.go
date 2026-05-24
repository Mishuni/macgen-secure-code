package main

import (
	"net/http"
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	r.POST("/decideUnsubscribe", func(c *gin.Context) {
		var emailContent string
		if err := c.ShouldBindBodyWith(&emailContent, binding.TextPlain); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
			return
		}

		email := extractEmail(emailContent)
		unsubscribe := shouldUnsubscribe(emailContent)

		c.JSON(http.StatusOK, gin.H{
			"email":      email,
			"unsubscribe": unsubscribe,
		})
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

func shouldUnsubscribe(content string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	contentLower := strings.ToLower(content)

	for _, keyword := range keywords {
		if strings.Contains(contentLower, keyword) {
			return true
		}
	}
	return false
}