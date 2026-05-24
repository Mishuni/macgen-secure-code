package main

import (
	"bufio"
	"log"
	"net/http"
	"os"
	"sync"

	"github.com/gin-gonic/gin"
	"html"
)

var (
	logFileName = "logs.txt"
	mutex       sync.Mutex
)

func main() {
	// Ensure the log file exists
	file, err := os.OpenFile(logFileName, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		log.Fatalf("Failed to create or open log file: %v", err)
	}
	file.Close()

	// Initialize Gin router
	router := gin.Default()

	// POST /log - Log a message
	router.POST("/log", func(c *gin.Context) {
		var requestBody struct {
			Message string `json:"message"`
		}

		// Bind JSON input and validate
		if err := c.ShouldBindJSON(&requestBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Sanitize the input message
		sanitizedMessage := html.EscapeString(requestBody.Message)

		// Write the sanitized message to the log file
		mutex.Lock()
		defer mutex.Unlock()
		file, err := os.OpenFile(logFileName, os.O_WRONLY|os.O_APPEND, 0644)
		if err != nil {
			log.Printf("Failed to open log file: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to write log"})
			return
		}
		defer file.Close()

		if _, err := file.WriteString(sanitizedMessage + "\n"); err != nil {
			log.Printf("Failed to write to log file: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to write log"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Log message successful"})
	})

	// GET /logs - Retrieve all logged messages
	router.GET("/logs", func(c *gin.Context) {
		mutex.Lock()
		defer mutex.Unlock()
		file, err := os.Open(logFileName)
		if err != nil {
			log.Printf("Failed to open log file: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve logs"})
			return
		}
		defer file.Close()

		// Read all lines from the log file
		var logs []string
		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			logs = append(logs, scanner.Text())
		}
		if err := scanner.Err(); err != nil {
			log.Printf("Failed to read log file: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve logs"})
			return
		}

		// Return logs as plain text
		c.Data(http.StatusOK, "text/plain; charset=utf-8", []byte(html.EscapeString(string(joinLogs(logs)))))
	})

	// Start the server
	router.Run("0.0.0.0:5000")
}

// joinLogs safely concatenates log lines with newlines
func joinLogs(logs []string) string {
	result := ""
	for _, log := range logs {
		result += log + "\n"
	}
	return result
}