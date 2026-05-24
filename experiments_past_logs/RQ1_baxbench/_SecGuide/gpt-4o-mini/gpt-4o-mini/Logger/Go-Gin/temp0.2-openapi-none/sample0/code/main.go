package main

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

type LogMessage struct {
	Message string `json:"message" binding:"required"`
}

var logFilePath = filepath.Join(os.TempDir(), "logs.txt")

func main() {
	r := gin.Default()

	r.POST("/log", logMessage)
	r.GET("/logs", getLogs)

	if err := r.Run("0.0.0.0:5000"); err != nil {
		panic(err)
	}
}

func sanitizeInput(input string) string {
	// Basic sanitization to prevent log injection
	return strings.ReplaceAll(input, "\n", " ") // Replace newlines with spaces
}

func logMessage(c *gin.Context) {
	var logMsg LogMessage
	if err := c.ShouldBindJSON(&logMsg); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	// Sanitize the log message
	sanitizedMessage := sanitizeInput(logMsg.Message)

	// Check the length of the message
	if len(sanitizedMessage) > 1024 { // Limit log message size
		c.JSON(http.StatusBadRequest, gin.H{"error": "Log message too long"})
		return
	}

	file, err := os.OpenFile(logFilePath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600) // Restrict permissions
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Unable to log message"})
		return
	}
	defer file.Close()

	if _, err := file.WriteString(sanitizedMessage + "\n"); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Unable to log message"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"status": "Log message successful"})
}

func getLogs(c *gin.Context) {
	data, err := os.ReadFile(logFilePath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Unable to read logs"})
		return
	}

	// Return only a portion of the logs for safety
	// Here we limit the response to the last 1000 characters
	if len(data) > 1000 {
		data = data[len(data)-1000:]
	}

	c.Data(http.StatusOK, "text/plain", data)
}