package main

import (
	"database/sql"
	"html/template"
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
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "./db.sqlite3"
	}
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Printf("Error opening database: %v", err)
		return
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
		log.Printf("Error creating table: %v", err)
		return
	}

	// Define routes
	router.GET("/messages", func(c *gin.Context) {
		limit := c.DefaultQuery("limit", "10")
		offset := c.DefaultQuery("offset", "0")
		sort := c.DefaultQuery("sort", "DESC")

		limitInt, err := strconv.Atoi(limit)
		if err != nil || limitInt < 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid limit"})
			return
		}

		offsetInt, err := strconv.Atoi(offset)
		if err != nil || offsetInt < 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid offset"})
			return
		}

		if sort != "ASC" && sort != "DESC" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid sort"})
			return
		}

		query := "SELECT content, username FROM messages ORDER BY created_at " + sort + " LIMIT ? OFFSET ?"
		rows, err := db.Query(query, limitInt, offsetInt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not retrieve messages"})
			return
		}
		defer rows.Close()

		var messages []Message
		for rows.Next() {
			var msg Message
			if err := rows.Scan(&msg.Content, &msg.Username); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not read message"})
				return
			}
			messages = append(messages, msg)
		}

		c.HTML(http.StatusOK, "messages.html", gin.H{
			"messages": messages,
		})
	})

	router.POST("/messages", func(c *gin.Context) {
		var msg Message
		if err := c.ShouldBindJSON(&msg); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		if len(msg.Content) > 500 || len(msg.Username) > 100 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Input too long"})
			return
		}

		_, err := db.Exec("INSERT INTO messages (content, username) VALUES (?, ?)", msg.Content, msg.Username)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not save message"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "Message posted successfully"})
	})

	// Load HTML templates with escaping
	router.SetHTMLTemplate(template.Must(template.New("").Parse(`
		<!DOCTYPE html>
		<html>
		<head>
			<title>Messages</title>
		</head>
		<body>
			<h1>Messages</h1>
			<ul>
				{{range .messages}}
					<li><strong>{{.Username}}</strong>: {{.Content}}</li>
				{{end}}
			</ul>
		</body>
		</html>
	`)))

	// Start the server
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Printf("Error starting server: %v", err)
	}
}