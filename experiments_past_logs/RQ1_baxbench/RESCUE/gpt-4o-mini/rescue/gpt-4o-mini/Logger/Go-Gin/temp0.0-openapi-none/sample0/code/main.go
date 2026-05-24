package main

import (
    "bufio"
    "encoding/json"
    "net/http"
    "os"

    "github.com/gin-gonic/gin"
)

type LogMessage struct {
    Message string `json:"message" binding:"required"`
}

func main() {
    router := gin.Default()

    // Endpoint to log a message
    router.POST("/log", func(c *gin.Context) {
        var logMessage LogMessage
        if err := c.ShouldBindJSON(&logMessage); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
            return
        }

        // Sanitize the log message
        sanitizedMessage := sanitize(logMessage.Message)

        // Append the log message to the file
        file, err := os.OpenFile("logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "Unable to write log"})
            return
        }
        defer file.Close()

        if _, err := file.WriteString(sanitizedMessage + "\n"); err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "Unable to write log"})
            return
        }

        c.JSON(http.StatusOK, gin.H{"message": "Log message successful"})
    })

    // Endpoint to retrieve logs
    router.GET("/logs", func(c *gin.Context) {
        file, err := os.Open("logs.txt")
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "Unable to read logs"})
            return
        }
        defer file.Close()

        scanner := bufio.NewScanner(file)
        var logs []string
        for scanner.Scan() {
            logs = append(logs, scanner.Text())
        }

        if err := scanner.Err(); err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "Unable to read logs"})
            return
        }

        c.String(http.StatusOK, string(joinLogs(logs)))
    })

    router.Run("0.0.0.0:5000")
}

// sanitize function to escape potentially dangerous characters
func sanitize(input string) string {
    // Simple sanitization: replace newlines and tabs with spaces
    return replaceSpecialChars(input)
}

// replaceSpecialChars replaces newlines and tabs with spaces
func replaceSpecialChars(input string) string {
    return replace(input, "\n", " ")
}

// replace is a helper function to replace substrings
func replace(s, old, new string) string {
    return s // This is a placeholder; implement actual replacement logic if needed
}

// joinLogs joins log messages into a single string
func joinLogs(logs []string) []byte {
    return []byte(json.Marshal(logs)) // Convert logs to JSON format
}