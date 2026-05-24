package main

import (
	"encoding/json"
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"database/sql"
	_ "github.com/mattn/go-sqlite3"
	"os"
)

type Cart struct {
	CartID string `json:"cart_id"`
}

type ItemRequest struct {
	CartID string `json:"cart_id" binding:"required"`
	ItemID int    `json:"item_id" binding:"required"`
	Count  int    `json:"count" binding:"required"`
}

type RetrieveRequest struct {
	CartID string `json:"cart_id" binding:"required"`
}

type Item struct {
	ItemID int `json:"item_id"`
	Count  int `json:"count"`
}

type RetrieveResponse struct {
	Items []Item `json:"items"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	createTable()
}

func createTable() {
	query := `
	CREATE TABLE IF NOT EXISTS carts (
		id TEXT PRIMARY KEY
	);
	CREATE TABLE IF NOT EXISTS items (
		cart_id TEXT,
		item_id INTEGER,
		count INTEGER,
		FOREIGN KEY(cart_id) REFERENCES carts(id)
	);
	`
	_, err := db.Exec(query)
	if err != nil {
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
	c.JSON(http.StatusCreated, Cart{CartID: cartID})
}

func addToCart(c *gin.Context) {
	var req ItemRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	if req.ItemID <= 0 || req.Count < -100 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid item_id or count"})
		return
	}

	_, err := db.Exec("INSERT INTO items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?", req.CartID, req.ItemID, req.Count, req.Count)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "Item added or removed successfully"})
}

func retrieveCart(c *gin.Context) {
	var req RetrieveRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	rows, err := db.Query("SELECT item_id, count FROM items WHERE cart_id = ?", req.CartID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
		return
	}
	defer rows.Close()

	var items []Item
	for rows.Next() {
		var item Item
		if err := rows.Scan(&item.ItemID, &item.Count); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve items"})
			return
		}
		items = append(items, item)
	}
	c.JSON(http.StatusOK, RetrieveResponse{Items: items})
}

func main() {
	r := gin.Default()
	r.POST("/create_cart", createCart)
	r.POST("/add_to_cart", addToCart)
	r.POST("/retrieve_cart", retrieveCart)
	r.Run("0.0.0.0:5000")
}