package main

import (
	"net/http"
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()
	router.POST("/decideUnsubscribe", decideUnsubscribe)
	router.Run("0.0.0.0:5000")
}

func decideUnsubscribe(c *gin.Context) {
	rawEmail, err := c.GetRawData()
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	emailContent := string(rawEmail)
	fromEmail := extractEmail(emailContent)
	unsubscribe := checkUnsubscribeKeywords(emailContent)

	c.JSON(http.StatusOK, gin.H{
		"email":      fromEmail,
		"unsubscribe": unsubscribe,
	})
}

func extractEmail(emailContent string) string {
	lines := strings.Split(emailContent, "\n")
	emailRegex := regexp.MustCompile(`(?i)^from:\s*.*<([^>]+)>`)
	for _, line := range lines {
		if matches := emailRegex.FindStringSubmatch(line); matches != nil {
			return matches[1]
		}
	}
	return ""
}

func checkUnsubscribeKeywords(emailContent string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	emailContentLower := strings.ToLower(emailContent)
	for _, keyword := range keywords {
		if strings.Contains(emailContentLower, keyword) {
			return true
		}
	}
	return false
}