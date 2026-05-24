package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize the database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	// Initialize Gin router
	r := gin.Default()

	// Routes
	r.POST("/create_cart", func(c *gin.Context) {
		cartID := uuid.New().String()
		_, err := db.Exec("INSERT INTO carts (id) VALUES (?)", cartID)
		if err != nil {
			log.Printf("Failed to create cart: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create cart"})
			return
		}
		c.JSON(http.StatusCreated, gin.H{"cart_id": cartID})
	})

	r.POST("/add_to_cart", func(c *gin.Context) {
		var request struct {
			CartID string `json:"cart_id" binding:"required"`
			ItemID int    `json:"item_id" binding:"required"`
			Count  int    `json:"count" binding:"required"`
		}
		if err := c.ShouldBindJSON(&request); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		// Check if cart exists
		var exists bool
		err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id = ?)", request.CartID).Scan(&exists)
		if err != nil || !exists {
			c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
			return
		}

		// Update or insert item in the cart
		_, err = db.Exec(`
			INSERT INTO cart_items (cart_id, item_id, count)
			VALUES (?, ?, ?)
			ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + excluded.count
		`, request.CartID, request.ItemID, request.Count)
		if err != nil {
			log.Printf("Failed to update cart: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update cart"})
			return
		}

		// Remove items with count <= 0
		_, err = db.Exec("DELETE FROM cart_items WHERE cart_id = ? AND item_id = ? AND count <= 0", request.CartID, request.ItemID)
		if err != nil {
			log.Printf("Failed to clean up cart: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to clean up cart"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Item added or removed successfully"})
	})

	r.POST("/retrieve_cart", func(c *gin.Context) {
		var request struct {
			CartID string `json:"cart_id" binding:"required"`
		}
		if err := c.ShouldBindJSON(&request); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		// Check if cart exists
		var exists bool
		err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id = ?)", request.CartID).Scan(&exists)
		if err != nil || !exists {
			c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
			return
		}

		// Retrieve items in the cart
		rows, err := db.Query("SELECT item_id, count FROM cart_items WHERE cart_id = ?", request.CartID)
		if err != nil {
			log.Printf("Failed to retrieve cart: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cart"})
			return
		}
		defer rows.Close()

		var items []gin.H
		for rows.Next() {
			var itemID, count int
			if err := rows.Scan(&itemID, &count); err != nil {
				log.Printf("Failed to scan row: %v", err)
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cart"})
				return
			}
			items = append(items, gin.H{"item_id": itemID, "count": count})
		}

		c.JSON(http.StatusOK, gin.H{"items": items})
	})

	// Start the server
	port := "5000"
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}
	r.Run("0.0.0.0:" + port)
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS carts (
			id TEXT PRIMARY KEY
		);
		CREATE TABLE IF NOT EXISTS cart_items (
			cart_id TEXT,
			item_id INTEGER,
			count INTEGER,
			PRIMARY KEY (cart_id, item_id),
			FOREIGN KEY (cart_id) REFERENCES carts(id)
		);
	`)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}