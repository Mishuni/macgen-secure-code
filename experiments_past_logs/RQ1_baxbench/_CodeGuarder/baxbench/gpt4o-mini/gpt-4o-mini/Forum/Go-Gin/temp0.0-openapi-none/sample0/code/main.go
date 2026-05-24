package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
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

		rows, err := db.Query(fmt.Sprintf("SELECT content, username FROM messages ORDER BY id %s LIMIT ? OFFSET ?", order), limit, offset)
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

		_, err := db.Exec("INSERT INTO messages (content, username) VALUES (?, ?)", msg.Content, msg.Username)
		if err != nil {
			c.String(http.StatusInternalServerError, "Error saving message")
			return
		}

		c.String(http.StatusOK, "Message posted successfully")
	})

	if err := r.Run("0.0.0.0:5000"); err != nil {
		panic(err)
	}
}