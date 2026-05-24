package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Gin router
	router := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create the messages table if it doesn't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS messages (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL,
			content TEXT NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Define routes
	router.GET("/messages", func(c *gin.Context) {
		// Parse query parameters
		limit := 10
		offset := 0
		sort := "DESC"

		if l := c.Query("limit"); l != "" {
			if parsedLimit, err := strconv.Atoi(l); err == nil && parsedLimit > 0 {
				limit = parsedLimit
			}
		}

		if o := c.Query("offset"); o != "" {
			if parsedOffset, err := strconv.Atoi(o); err == nil && parsedOffset >= 0 {
				offset = parsedOffset
			}
		}

		if s := c.Query("sort"); s != "" {
			if strings.ToUpper(s) == "ASC" || strings.ToUpper(s) == "DESC" {
				sort = strings.ToUpper(s)
			}
		}

		// Query the database securely using parameterized queries
		query := `SELECT username, content, created_at FROM messages ORDER BY created_at ` + sort + ` LIMIT ? OFFSET ?`
		rows, err := db.Query(query, limit, offset)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch messages"})
			return
		}
		defer rows.Close()

		// Collect results
		var messages []gin.H
		for rows.Next() {
			var username, content, createdAt string
			if err := rows.Scan(&username, &content, &createdAt); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse messages"})
				return
			}
			messages = append(messages, gin.H{
				"username":   username,
				"content":    content,
				"created_at": createdAt,
			})
		}

		// Return results
		c.JSON(http.StatusOK, messages)
	})

	router.POST("/messages", func(c *gin.Context) {
		// Parse JSON body
		var message struct {
			Username string `json:"username" binding:"required"`
			Content  string `json:"content" binding:"required"`
		}
		if err := c.ShouldBindJSON(&message); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		// Insert the message into the database securely using parameterized queries
		query := `INSERT INTO messages (username, content) VALUES (?, ?)`
		_, err := db.Exec(query, message.Username, message.Content)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to post message"})
			return
		}

		// Return success response
		c.JSON(http.StatusOK, gin.H{"message": "Message posted successfully"})
	})

	// Start the server
	port := "5000"
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}
	router.Run("0.0.0.0:" + port)
}