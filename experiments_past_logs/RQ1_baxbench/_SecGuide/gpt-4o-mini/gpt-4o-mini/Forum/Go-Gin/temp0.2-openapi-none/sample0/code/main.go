package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"
	"strconv"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Message struct {
	Content  string `json:"content" binding:"required"`
	Username string `json:"username" binding:"required"`
}

func main() {
	r := gin.Default()
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		// Log the error and exit
		gin.DefaultWriter.Write([]byte("Error opening database: " + err.Error() + "\n"))
		os.Exit(1)
	}
	defer db.Close()

	// Create messages table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT NOT NULL,
		username TEXT NOT NULL
	)`)
	if err != nil {
		// Log the error and exit
		gin.DefaultWriter.Write([]byte("Error creating table: " + err.Error() + "\n"))
		os.Exit(1)
	}

	r.GET("/messages", func(c *gin.Context) {
		limit, _ := strconv.Atoi(c.DefaultQuery("limit", "10"))
		offset, _ := strconv.Atoi(c.DefaultQuery("offset", "0"))
		sort := c.DefaultQuery("sort", "DESC")

		// Validate sort parameter
		validSortOptions := map[string]bool{"ASC": true, "DESC": true}
		if !validSortOptions[sort] {
			sort = "DESC" // Default to DESC if invalid
		}

		rows, err := db.Query("SELECT content, username FROM messages ORDER BY id " + sort + " LIMIT ? OFFSET ?", limit, offset)
		if err != nil {
			c.String(http.StatusInternalServerError, "Error retrieving messages")
			return
		}
		defer rows.Close()

		var messages []Message
		for rows.Next() {
			var msg Message
			if err := rows.Scan(&msg.Content, &msg.Username); err != nil {
				c.String(http.StatusInternalServerError, "Error scanning message")
				return
			}
			messages = append(messages, msg)
		}

		c.JSON(http.StatusOK, messages)
	})

	r.POST("/messages", func(c *gin.Context) {
		var msg Message
		if err := c.ShouldBindJSON(&msg); err != nil {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}

		// Validate input length
		if len(msg.Content) > 500 || len(msg.Username) > 100 {
			c.String(http.StatusBadRequest, "Input too long")
			return
		}

		// Sanitize content to prevent XSS
		msg.Content = sanitizeInput(msg.Content)

		_, err := db.Exec("INSERT INTO messages (content, username) VALUES (?, ?)", msg.Content, msg.Username)
		if err != nil {
			c.String(http.StatusInternalServerError, "Error posting message")
			return
		}

		c.String(http.StatusOK, "Message posted successfully")
	})

	// CORS configuration
	r.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "https://yourdomain.com") // Adjust this to restrict origins
		c.Header("Access-Control-Allow-Methods", "GET, POST")
		c.Header("Access-Control-Allow-Headers", "Content-Type")
		c.Next()
	})

	r.Run("0.0.0.0:5000")
}

// sanitizeInput is a simple function to sanitize user input
func sanitizeInput(input string) string {
	// Implement sanitization logic here (e.g., escaping HTML)
	return input // Placeholder, implement actual sanitization
}