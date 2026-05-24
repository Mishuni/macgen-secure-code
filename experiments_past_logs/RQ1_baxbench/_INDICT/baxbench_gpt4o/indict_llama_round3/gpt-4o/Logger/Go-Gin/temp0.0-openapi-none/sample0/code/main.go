package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
	"os"
)

const logFileName = "logs.txt"

func main() {
	r := gin.Default()

	r.POST("/log", func(c *gin.Context) {
		var json struct {
			Message string `json:"message" binding:"required"`
		}

		if err := c.ShouldBindJSON(&json); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		file, err := os.OpenFile(logFileName, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not open log file"})
			return
		}
		defer file.Close()

		if _, err := file.WriteString(json.Message + "\n"); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not write to log file"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "Log message successful"})
	})

	r.GET("/logs", func(c *gin.Context) {
		data, err := os.ReadFile(logFileName)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not read log file"})
			return
		}

		c.Data(http.StatusOK, "text/plain", data)
	})

	r.Run("0.0.0.0:5000")
}