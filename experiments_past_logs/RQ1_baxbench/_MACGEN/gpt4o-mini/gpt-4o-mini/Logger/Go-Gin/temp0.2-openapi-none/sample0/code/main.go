package main

import (
	"io/ioutil"
	"net/http"
	"os"
	"regexp"

	"github.com/gin-gonic/gin"
)

type LogMessage struct {
	Message string `json:"message"`
}

func main() {
	router := gin.Default()

	router.POST("/log", func(c *gin.Context) {
		var logMessage LogMessage
		if err := c.ShouldBindJSON(&logMessage); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Input validation
		if len(logMessage.Message) > 1024 || containsControlCharacters(logMessage.Message) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Log message too long or contains invalid characters"})
			return
		}

		// Sanitize log message to prevent log injection
		logMessage.Message = regexp.MustCompile(`\n`).ReplaceAllString(logMessage.Message, " ")

		file, err := os.OpenFile("logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600) // Set permissions to 0600
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Unable to open log file"})
			return
		}
		defer file.Close()

		if _, err := file.WriteString(logMessage.Message + "\n"); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Unable to write to log file"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "Log message successful"})
	})

	router.GET("/logs", func(c *gin.Context) {
		data, err := ioutil.ReadFile("logs.txt")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Unable to read log file"})
			return
		}

		c.String(http.StatusOK, string(data))
	})

	router.Run("0.0.0.0:5000")
}

func containsControlCharacters(s string) bool {
	re := regexp.MustCompile(`[\x00-\x1F\x7F]`)
	return re.MatchString(s)
}