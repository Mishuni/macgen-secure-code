package main

import (
	"github.com/gin-gonic/gin"
	"html"
	"io"
	"log"
	"net/http"
	"os"
	"sync"
)

const logFileName = "logs.txt"

var logMutex sync.Mutex

func main() {
	// Initialize Gin router
	router := gin.Default()

	// POST /log endpoint to log a message
	router.POST("/log", func(c *gin.Context) {
		var json struct {
			Message string `json:"message" binding:"required"`
		}

		if err := c.ShouldBindJSON(&json); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
			return
		}

		// Sanitize and validate the message
		if len(json.Message) == 0 || len(json.Message) > 1024 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Message must be between 1 and 1024 characters"})
			return
		}

		// Escape potentially harmful characters
		sanitizedMessage := html.EscapeString(json.Message)

		// Append the log message to the log file
		logMutex.Lock()
		defer logMutex.Unlock()

		file, err := os.OpenFile(logFileName, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600)
		if err != nil {
			log.Printf("Failed to open log file: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to log message"})
			return
		}
		defer file.Close()

		if _, err := file.WriteString(sanitizedMessage + "\n"); err != nil {
			log.Printf("Failed to write to log file: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to log message"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "Log message successful"})
	})

	// GET /logs endpoint to retrieve all logged messages
	router.GET("/logs", func(c *gin.Context) {
		logMutex.Lock()
		defer logMutex.Unlock()

		file, err := os.Open(logFileName)
		if err != nil {
			log.Printf("Failed to read log file: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve logs"})
			return
		}
		defer file.Close()

		data, err := io.ReadAll(file)
		if err != nil {
			log.Printf("Failed to read log file: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve logs"})
			return
		}

		c.Data(http.StatusOK, "text/plain", data)
	})

	// Start the server on port 5000
	router.Run("0.0.0.0:5000")
}