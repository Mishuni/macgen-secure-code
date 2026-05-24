package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
)

const logFilePath = "logs.txt"

func main() {
	router := gin.Default()

	router.POST("/log", logMessage)
	router.GET("/logs", getLogs)

	if err := router.Run("0.0.0.0:5000"); err != nil {
		fmt.Printf("Failed to start server: %v\n", err)
	}
}

func logMessage(c *gin.Context) {
	var json struct {
		Message string `json:"message" binding:"required"`
	}

	if err := c.ShouldBindJSON(&json); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	if err := appendToFile(logFilePath, json.Message); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to log message"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"status": "Log message successful"})
}

func getLogs(c *gin.Context) {
	logs, err := ioutil.ReadFile(logFilePath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve logs"})
		return
	}

	c.Data(http.StatusOK, "text/plain", logs)
}

func appendToFile(filePath, message string) error {
	f, err := os.OpenFile(filePath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer f.Close()

	if _, err := f.WriteString(message + "\n"); err != nil {
		return err
	}
	return nil
}