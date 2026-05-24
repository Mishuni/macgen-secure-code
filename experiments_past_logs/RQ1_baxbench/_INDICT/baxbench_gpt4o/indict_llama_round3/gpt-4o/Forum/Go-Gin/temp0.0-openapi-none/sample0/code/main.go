package main

import (
	"database/sql"
	"html/template"
	"log"
	"net/http"
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
	r := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
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
		log.Fatal(err)
	}

	// Define routes
	r.GET("/messages", func(c *gin.Context) {
		limit := c.DefaultQuery("limit", "10")
		offset := c.DefaultQuery("offset", "0")
		sort := c.DefaultQuery("sort", "desc")

		limitInt, err := strconv.Atoi(limit)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid limit"})
			return
		}

		offsetInt, err := strconv.Atoi(offset)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid offset"})
			return
		}

		if sort != "ASC" && sort != "DESC" && sort != "asc" && sort != "desc" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid sort"})
			return
		}

		rows, err := db.Query(`SELECT content, username FROM messages ORDER BY created_at `+sort+` LIMIT ? OFFSET ?`, limitInt, offsetInt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database query error"})
			return
		}
		defer rows.Close()

		var messages []Message
		for rows.Next() {
			var message Message
			if err := rows.Scan(&message.Content, &message.Username); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Database scan error"})
				return
			}
			messages = append(messages, message)
		}

		tmpl := `<html><body><h1>Messages</h1><ul>{{range .}}<li><strong>{{.Username}}</strong>: {{.Content}}</li>{{end}}</ul></body></html>`
		t, err := template.New("messages").Parse(tmpl)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Template parsing error"})
			return
		}

		c.Header("Content-Type", "text/html")
		if err := t.Execute(c.Writer, messages); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Template execution error"})
			return
		}
	})

	r.POST("/messages", func(c *gin.Context) {
		var newMessage Message
		if err := c.ShouldBindJSON(&newMessage); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		_, err := db.Exec(`INSERT INTO messages (content, username) VALUES (?, ?)`, newMessage.Content, newMessage.Username)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database insert error"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "Message posted successfully"})
	})

	// Start the server
	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatal("Unable to start:", err)
	}
}