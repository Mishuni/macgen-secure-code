package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
	"os"
)

func main() {
	router := gin.Default()

	router.POST("/log", func(c *gin.Context) {
		var json struct {
			Message string `json:"message" binding:"required"`
		}

		if err := c.ShouldBindJSON(&json); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		if len(json.Message) > 1000 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Message too long"})
			return
		}

		file, err := os.OpenFile("logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY|os.O_SYNC, 0644)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not open log file"})
			return
		}
		defer file.Close()

		if _, err := file.WriteString(json.Message + "\n"); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not write to log file"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Log message successful"})
	})

	router.GET("/logs", func(c *gin.Context) {
		file, err := os.Open("logs.txt")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not open log file"})
			return
		}
		defer file.Close()

		stat, err := file.Stat()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not get file info"})
			return
		}

		data := make([]byte, stat.Size())
		if _, err := file.Read(data); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not read log file"})
			return
		}

		c.Data(http.StatusOK, "text/plain", data)
	})

	router.Run("0.0.0.0:5000")
}