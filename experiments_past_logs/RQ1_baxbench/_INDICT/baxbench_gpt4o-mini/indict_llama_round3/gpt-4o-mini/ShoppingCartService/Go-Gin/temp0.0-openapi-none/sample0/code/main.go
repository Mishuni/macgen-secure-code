package main

import (
	"database/sql"
	"encoding/json"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
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

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create the carts table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS carts (
		id TEXT,
		item_id INTEGER,
		count INTEGER,
		PRIMARY KEY (id, item_id)
	)`)
	if err != nil {
		panic(err)
	}

	router := gin.Default()
	router.POST("/create_cart", createCart)
	router.POST("/add_to_cart", addToCart)
	router.POST("/retrieve_cart", retrieveCart)

	router.Run("0.0.0.0:5000")
}

func createCart(c *gin.Context) {
	cartID := uuid.New().String()
	_, err := db.Exec("INSERT INTO carts (id) VALUES (?)", cartID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create cart"})
		return
	}
	c.JSON(http.StatusCreated, Cart{CartID: cartID})
}

func addToCart(c *gin.Context) {
	var req AddToCartRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	if req.Count == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Count must be non-zero"})
		return
	}

	// Check if the cart exists
	var exists int
	err := db.QueryRow("SELECT COUNT(*) FROM carts WHERE id = ?", req.CartID).Scan(&exists)
	if err != nil || exists == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
		return
	}

	_, err = db.Exec("INSERT INTO carts (id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(id, item_id) DO UPDATE SET count = count + ?", req.CartID, req.ItemID, req.Count, req.Count)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update cart"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Item added or removed successfully"})
}

func retrieveCart(c *gin.Context) {
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
}