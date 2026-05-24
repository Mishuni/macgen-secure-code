package main

import (
	"database/sql"
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
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT NOT NULL,
		username TEXT NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)`)
	if err != nil {
		log.Fatal(err)
	}

	r := gin.Default()

	r.GET("/messages", func(c *gin.Context) {
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

		query := `SELECT content, username FROM messages ORDER BY created_at ` + sort + ` LIMIT ? OFFSET ?`
		rows, err := db.Query(query, limitInt, offsetInt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database query error"})
			return
		}
		defer rows.Close()

		var messages []Message
		for rows.Next() {
			var msg Message
			if err := rows.Scan(&msg.Content, &msg.Username); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Database scan error"})
				return
			}
			messages = append(messages, msg)
		}

		c.HTML(http.StatusOK, "messages.html", gin.H{"messages": messages})
	})

	r.POST("/messages", func(c *gin.Context) {
		var msg Message
		if err := c.ShouldBindJSON(&msg); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		_, err := db.Exec(`INSERT INTO messages (content, username) VALUES (?, ?)`, msg.Content, msg.Username)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database insert error"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "Message posted successfully"})
	})

	r.Run("0.0.0.0:5000")
}