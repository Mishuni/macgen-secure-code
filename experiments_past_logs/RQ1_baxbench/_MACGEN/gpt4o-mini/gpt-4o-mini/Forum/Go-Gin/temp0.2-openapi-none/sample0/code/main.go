package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"
	"regexp"
	"strconv"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

type Message struct {
	Content  string `json:"content" example:"hello world!"`
	Username string `json:"username" example:"alice"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT,
		username TEXT,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func sanitizeInput(input string) string {
	re := regexp.MustCompile(`<[^>]*>`)
	return re.ReplaceAllString(input, "")
}

func getMessages(c *gin.Context) {
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "10"))
	offset, _ := strconv.Atoi(c.DefaultQuery("offset", "0"))
	sort := c.DefaultQuery("sort", "DESC")

	if limit <= 0 {
		limit = 10
	}
	if offset < 0 {
		offset = 0
	}
	if sort != "ASC" && sort != "DESC" {
		sort = "DESC"
	}

	rows, err := db.Query("SELECT content, username FROM messages ORDER BY created_at " + sort + " LIMIT ? OFFSET ?", limit, offset)
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
	if err := c.ShouldBindJSON(&msg); err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	msg.Content = sanitizeInput(msg.Content)

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
	r.Run("0.0.0.0:5000")
}