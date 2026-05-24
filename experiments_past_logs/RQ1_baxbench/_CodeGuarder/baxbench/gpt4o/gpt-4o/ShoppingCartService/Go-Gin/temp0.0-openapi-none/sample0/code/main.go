package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Cart struct {
	ID string `json:"cart_id"`
}

type CartItem struct {
	CartID string `json:"cart_id"`
	ItemID int    `json:"item_id"`
	Count  int    `json:"count"`
}

type RetrieveCartRequest struct {
	CartID string `json:"cart_id"`
}

type RetrieveCartResponse struct {
	Items []CartItem `json:"items"`
}

func main() {
	// Initialize Gin router
	router := gin.Default()

	// Initialize database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create tables if they don't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS carts (id TEXT PRIMARY KEY)`)
	if err != nil {
		log.Fatalf("Failed to create carts table: %v", err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS cart_items (cart_id TEXT, item_id INTEGER, count INTEGER, PRIMARY KEY(cart_id, item_id))`)
	if err != nil {
		log.Fatalf("Failed to create cart_items table: %v", err)
	}

	// Define routes
	router.POST("/create_cart", func(c *gin.Context) {
		cartID := uuid.New().String()
		_, err := db.Exec("INSERT INTO carts (id) VALUES (?)", cartID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create cart"})
			return
		}
		c.JSON(http.StatusCreated, gin.H{"cart_id": cartID})
	})

	router.POST("/add_to_cart", func(c *gin.Context) {
		var item CartItem
		if err := c.ShouldBindJSON(&item); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		// Check if cart exists
		var cartExists bool
		err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id=?)", item.CartID).Scan(&cartExists)
		if err != nil || !cartExists {
			c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
			return
		}

		// Add or update item in cart
		_, err = db.Exec("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count=count+excluded.count", item.CartID, item.ItemID, item.Count)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update cart"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Item added or removed successfully"})
	})

	router.POST("/retrieve_cart", func(c *gin.Context) {
		var request RetrieveCartRequest
		if err := c.ShouldBindJSON(&request); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		// Retrieve items from cart
		rows, err := db.Query("SELECT item_id, count FROM cart_items WHERE cart_id=?", request.CartID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cart"})
			return
		}
		defer rows.Close()

		var items []CartItem
		for rows.Next() {
			var item CartItem
			if err := rows.Scan(&item.ItemID, &item.Count); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse cart items"})
				return
			}
			items = append(items, item)
		}

		if len(items) == 0 {
			c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
			return
		}

		c.JSON(http.StatusOK, RetrieveCartResponse{Items: items})
	})

	// Start server
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}