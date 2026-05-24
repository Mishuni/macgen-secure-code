package main

import (
	"encoding/json"
	"net/http"
	"os"
	"sync"

	"github.com/gin-gonic/gin"
)

const logFile = "logs.txt"

type LogMessage struct {
	Message string `json:"message"`
}

var mu sync.Mutex

func main() {
	r := gin.Default()

	r.POST("/log", func(c *gin.Context) {
		var logMessage LogMessage
		if err := c.ShouldBindJSON(&logMessage); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		mu.Lock()
		defer mu.Unlock()

		if err := appendLog(logMessage.Message); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to log message"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "Log message successful"})
	})

	r.GET("/logs", func(c *gin.Context) {
		mu.Lock()
		defer mu.Unlock()

		logs, err := os.ReadFile(logFile)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve logs"})
			return
		}

		c.Data(http.StatusOK, "text/plain", logs)
	})

	r.Run("0.0.0.0:5000")
}

func appendLog(message string) error {
	f, err := os.OpenFile(logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer f.Close()

	if _, err := f.WriteString(message + "\n"); err != nil {
		return err
	}
	return nil
}