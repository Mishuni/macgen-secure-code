package main

import (
	"encoding/json"
	"net/http"
	"os"
	"strconv"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"database/sql"
)

type Message struct {
	Content  string `json:"content" example:"hello world!"`
	Username string `json:"username" example:"alice"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT,
		username TEXT
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func getMessages(c *gin.Context) {
	limit, err := strconv.Atoi(c.DefaultQuery("limit", "10"))
	if err != nil || limit <= 0 {
		limit = 10
	}
	offset, err := strconv.Atoi(c.DefaultQuery("offset", "0"))
	if err != nil || offset < 0 {
		offset = 0
	}
	sort := c.DefaultQuery("sort", "DESC")

	order := "DESC"
	if sort == "ASC" {
		order = "ASC"
	}

	rows, err := db.Query("SELECT content, username FROM messages ORDER BY id " + order + " LIMIT ? OFFSET ?", limit, offset)
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
}

func postMessage(c *gin.Context) {
	var msg Message
	if err := c.ShouldBindJSON(&msg); err != nil || msg.Content == "" || msg.Username == "" {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	_, err := db.Exec("INSERT INTO messages (content, username) VALUES (?, ?)", msg.Content, msg.Username)
	if err != nil {
		c.String(http.StatusInternalServerError, "Error saving message")
		return
	}

	c.String(http.StatusOK, "Message posted successfully")
}

func main() {
	r := gin.Default()
	r.GET("/messages", getMessages)
	r.POST("/messages", postMessage)

	if err := r.Run("0.0.0.0:5000"); err != nil {
		panic(err)
	}
}