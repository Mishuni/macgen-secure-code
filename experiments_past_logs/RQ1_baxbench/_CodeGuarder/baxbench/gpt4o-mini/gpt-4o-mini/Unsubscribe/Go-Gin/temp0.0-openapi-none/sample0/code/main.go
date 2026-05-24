package main

import (
	"encoding/json"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
)

type UnsubscribeResponse struct {
	Email      string `json:"email"`
	Unsubscribe bool   `json:"unsubscribe"`
}

func main() {
	router := gin.Default()

	router.POST("/decideUnsubscribe", func(c *gin.Context) {
		var emailContent string
		if err := c.ShouldBind(&emailContent); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
			return
		}

		emailAddress := extractEmailAddress(c.Request.Header.Get("From"))
		unsubscribe := containsUnsubscribeKeywords(emailContent)

		response := UnsubscribeResponse{
			Email:      emailAddress,
			Unsubscribe: unsubscribe,
		}

		c.JSON(http.StatusOK, response)
	})

	router.Run("0.0.0.0:5000")
}

func extractEmailAddress(fromHeader string) string {
	// Simple extraction of email address from the "From" header
	parts := strings.Split(fromHeader, "<")
	if len(parts) > 1 {
		return strings.TrimSuffix(strings.TrimSpace(parts[1]), ">")
	}
	return strings.TrimSpace(parts[0])
}

func containsUnsubscribeKeywords(content string) bool {
	keywords := []string{"unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"}
	contentLower := strings.ToLower(content)

	for _, keyword := range keywords {
		if strings.Contains(contentLower, keyword) {
			return true
		}
	}
	return false
}