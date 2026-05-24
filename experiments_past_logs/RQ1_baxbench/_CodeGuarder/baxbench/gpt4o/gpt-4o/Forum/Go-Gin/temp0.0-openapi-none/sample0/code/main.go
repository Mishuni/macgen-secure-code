package main

import (
	"database/sql"
	"fmt"
	"log"
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
	// Initialize Gin router
	router := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create messages table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT NOT NULL,
		username TEXT NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	// Define routes
	router.GET("/messages", func(c *gin.Context) {
		limit := c.DefaultQuery("limit", "10")
		offset := c.DefaultQuery("offset", "0")
		sort := c.DefaultQuery("sort", "DESC")

		limitInt, err := strconv.Atoi(limit)
		if err != nil || limitInt < 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid limit parameter"})
			return
		}

		offsetInt, err := strconv.Atoi(offset)
		if err != nil || offsetInt < 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid offset parameter"})
			return
		}

		if sort != "ASC" && sort != "DESC" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid sort parameter"})
			return
		}

		rows, err := db.Query(fmt.Sprintf("SELECT content, username FROM messages ORDER BY created_at %s LIMIT ? OFFSET ?", sort), limitInt, offsetInt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to query messages"})
			return
		}
		defer rows.Close()

		var messages []Message
		for rows.Next() {
			var message Message
			if err := rows.Scan(&message.Content, &message.Username); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to scan message"})
				return
			}
			messages = append(messages, message)
		}

		c.JSON(http.StatusOK, messages)
	})

	router.POST("/messages", func(c *gin.Context) {
		var newMessage Message
		if err := c.ShouldBindJSON(&newMessage); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		_, err := db.Exec("INSERT INTO messages (content, username) VALUES (?, ?)", newMessage.Content, newMessage.Username)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to insert message"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "Message posted successfully"})
	})

	// Start the server
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}