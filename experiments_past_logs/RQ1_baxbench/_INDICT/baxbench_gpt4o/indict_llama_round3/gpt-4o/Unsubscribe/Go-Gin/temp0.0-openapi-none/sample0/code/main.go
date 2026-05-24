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
		emailContent, err := c.GetRawData()
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		emailStr := string(emailContent)
		fromEmail := extractEmail(emailStr)
		if fromEmail == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Could not extract email"})
			return
		}

		unsubscribe := shouldUnsubscribe(emailStr)

		c.JSON(http.StatusOK, gin.H{
			"email":      fromEmail,
			"unsubscribe": unsubscribe,
		})
	})

	r.Run("0.0.0.0:5000")
}

func extractEmail(emailContent string) string {
	re := regexp.MustCompile(`(?m)^From:\s*.*<(.+?)>`)
	matches := re.FindStringSubmatch(emailContent)
	if len(matches) > 1 {
		return matches[1]
	}
	return ""
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