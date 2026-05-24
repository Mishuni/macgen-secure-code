package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Cart struct {
	ID    string `json:"cart_id"`
	Items []Item `json:"items"`
}

type Item struct {
	ItemID int `json:"item_id"`
	Count  int `json:"count"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS carts (
		id TEXT PRIMARY KEY,
		item_id INTEGER,
		count INTEGER
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}
}

func main() {
	r := gin.Default()

	r.POST("/create_cart", createCart)
	r.POST("/add_to_cart", addToCart)
	r.POST("/retrieve_cart", retrieveCart)

	if err := r.Run("0.0.0.0:5000"); err != nil {
		panic(err)
	}
}

func createCart(c *gin.Context) {
	cartID := uuid.New().String()
	_, err := db.Exec("INSERT INTO carts (id) VALUES (?)", cartID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create cart"})
		return
	}
	c.JSON(http.StatusCreated, gin.H{"cart_id": cartID})
}

func addToCart(c *gin.Context) {
	var request struct {
		CartID string `json:"cart_id" binding:"required"`
		ItemID int    `json:"item_id" binding:"required"`
		Count  int    `json:"count" binding:"required"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	if request.Count < 0 {
		_, err := db.Exec("DELETE FROM carts WHERE id = ? AND item_id = ?", request.CartID, request.ItemID)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
			return
		}
	} else {
		_, err := db.Exec("INSERT INTO carts (id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(id, item_id) DO UPDATE SET count = count + ?", request.CartID, request.ItemID, request.Count, request.Count)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
			return
		}
	}
	c.JSON(http.StatusOK, gin.H{"message": "Item added or removed successfully"})
}

func retrieveCart(c *gin.Context) {
	var request struct {
		CartID string `json:"cart_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	rows, err := db.Query("SELECT item_id, count FROM carts WHERE id = ?", request.CartID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
		return
	}
	defer rows.Close()

	var items []Item
	for rows.Next() {
		var item Item
		if err := rows.Scan(&item.ItemID, &item.Count); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cart items"})
			return
		}
		items = append(items, item)
	}

	c.JSON(http.StatusOK, gin.H{"items": items})
}