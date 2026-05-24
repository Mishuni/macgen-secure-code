package main

import (
	"bufio"
	"fmt"
	"log"
	"net/http"
	"os"
	"sync"

	"github.com/gin-gonic/gin"
)

const logFileName = "logs.txt"

var mu sync.Mutex

func main() {
	router := gin.Default()

	router.POST("/log", logMessage)
	router.GET("/logs", getLogs)

	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func logMessage(c *gin.Context) {
	var json struct {
		Message string `json:"message" binding:"required"`
	}

	if err := c.ShouldBindJSON(&json); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
		return
	}

	mu.Lock()
	defer mu.Unlock()

	file, err := os.OpenFile(logFileName, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open log file"})
		return
	}
	defer file.Close()

	if _, err := file.WriteString(json.Message + "\n"); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to write log message"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"status": "Log message successful"})
}

func getLogs(c *gin.Context) {
	mu.Lock()
	defer mu.Unlock()

	file, err := os.Open(logFileName)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open log file"})
		return
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	var logs string
	for scanner.Scan() {
		logs += scanner.Text() + "\n"
	}

	if err := scanner.Err(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read log file"})
		return
	}

	c.Data(http.StatusOK, "text/plain", []byte(logs))
}