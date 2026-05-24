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
	Content  string `json:"content"`
	Username string `json:"username"`
}

func main() {
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create messages table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT NOT NULL,
		username TEXT NOT NULL
	)`)
	if err != nil {
		panic(err)
	}

	r := gin.Default()

	r.GET("/messages", func(c *gin.Context) {
		limit, _ := strconv.Atoi(c.DefaultQuery("limit", "10"))
		offset, _ := strconv.Atoi(c.DefaultQuery("offset", "0"))
		sort := c.DefaultQuery("sort", "DESC")

		order := "DESC"
		if sort == "ASC" {
			order = "ASC"
		}

		rows, err := db.Query("SELECT content, username FROM messages ORDER BY id " + order + " LIMIT ? OFFSET ?", limit, offset)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch messages"})
			return
		}
		defer rows.Close()

		var messages []Message
		for rows.Next() {
			var msg Message
			if err := rows.Scan(&msg.Content, &msg.Username); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to scan message"})
				return
			}
			messages = append(messages, msg)
		}

		c.JSON(http.StatusOK, messages)
	})

	r.POST("/messages", func(c *gin.Context) {
		var msg Message
		if err := c.ShouldBindJSON(&msg); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		_, err := db.Exec("INSERT INTO messages (content, username) VALUES (?, ?)", msg.Content, msg.Username)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to post message"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "Message posted successfully"})
	})

	r.Run("0.0.0.0:5000")
}