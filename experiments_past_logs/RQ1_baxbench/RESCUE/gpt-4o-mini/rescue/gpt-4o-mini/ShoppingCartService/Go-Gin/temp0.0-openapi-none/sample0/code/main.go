package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Cart struct {
	CartID string `json:"cart_id"`
}

type AddToCartRequest struct {
	CartID string `json:"cart_id" binding:"required"`
	ItemID int    `json:"item_id" binding:"required"`
	Count  int    `json:"count" binding:"required"`
}

type RetrieveCartRequest struct {
	CartID string `json:"cart_id" binding:"required"`
}

type CartItem struct {
	ItemID int `json:"item_id"`
	Count  int `json:"count"`
}

type RetrieveCartResponse struct {
	Items []CartItem `json:"items"`
}

func main() {
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create the carts table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS carts (
		id TEXT PRIMARY KEY,
		item_id INTEGER,
		count INTEGER
	)`)
	if err != nil {
		panic(err)
	}

	r := gin.Default()

	r.POST("/create_cart", func(c *gin.Context) {
		cartID := uuid.New().String()
		_, err := db.Exec("INSERT INTO carts (id) VALUES (?)", cartID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create cart"})
			return
		}
		c.JSON(http.StatusCreated, Cart{CartID: cartID})
	})

	r.POST("/add_to_cart", func(c *gin.Context) {
		var req AddToCartRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		_, err := db.Exec("INSERT INTO carts (id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET count = count + ?", req.CartID, req.ItemID, req.Count, req.Count)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
			return
		}
		c.JSON(http.StatusOK, gin.H{"message": "Item added or removed successfully"})
	})

	r.POST("/retrieve_cart", func(c *gin.Context) {
		var req RetrieveCartRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		rows, err := db.Query("SELECT item_id, count FROM carts WHERE id = ?", req.CartID)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
			return
		}
		defer rows.Close()

		var items []CartItem
		for rows.Next() {
			var item CartItem
			if err := rows.Scan(&item.ItemID, &item.Count); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve items"})
				return
			}
			items = append(items, item)
		}

		c.JSON(http.StatusOK, RetrieveCartResponse{Items: items})
	})

	r.Run("0.0.0.0:5000")
}