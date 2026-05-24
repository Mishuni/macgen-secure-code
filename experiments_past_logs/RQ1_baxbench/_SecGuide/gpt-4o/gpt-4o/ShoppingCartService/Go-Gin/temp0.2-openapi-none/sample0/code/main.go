package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"github.com/joho/godotenv"
)

func main() {
	// Load environment variables from .env file
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	// Initialize Gin router
	router := gin.Default()

	// Connect to SQLite database
	dbPath := os.Getenv("DATABASE_PATH")
	if dbPath == "" {
		log.Fatal("DATABASE_PATH environment variable not set")
	}
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	// Define routes
	router.POST("/create_cart", func(c *gin.Context) {
		createCartHandler(c, db)
	})

	router.POST("/add_to_cart", func(c *gin.Context) {
		addToCartHandler(c, db)
	})

	router.POST("/retrieve_cart", func(c *gin.Context) {
		retrieveCartHandler(c, db)
	})

	// Start the server
	router.Run("0.0.0.0:5000")
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
			FOREIGN KEY(cart_id) REFERENCES carts(id),
			PRIMARY KEY(cart_id, item_id)
		);
	`)
	if err != nil {
		log.Fatal("Failed to create tables:", err)
	}
}

func createCartHandler(c *gin.Context, db *sql.DB) {
	cartID := uuid.New().String()
	_, err := db.Exec("INSERT INTO carts (id) VALUES (?)", cartID)
	if err != nil {
		log.Println("Error creating cart:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create cart"})
		return
	}
	c.JSON(http.StatusCreated, gin.H{"cart_id": cartID})
}

func addToCartHandler(c *gin.Context, db *sql.DB) {
	var request struct {
		CartID string `json:"cart_id" binding:"required"`
		ItemID int    `json:"item_id" binding:"required"`
		Count  int    `json:"count" binding:"required"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	if request.Count <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Count must be a positive integer"})
		return
	}

	// Check if cart exists
	var exists bool
	err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id=?)", request.CartID).Scan(&exists)
	if err != nil || !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
		return
	}

	// Update or insert item in cart
	_, err = db.Exec(`
		INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)
		ON CONFLICT(cart_id, item_id) DO UPDATE SET count=count+excluded.count
		WHERE count+excluded.count > 0
	`, request.CartID, request.ItemID, request.Count)
	if err != nil {
		log.Println("Error updating cart:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update cart"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Item added or removed successfully"})
}

func retrieveCartHandler(c *gin.Context, db *sql.DB) {
	var request struct {
		CartID string `json:"cart_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	// Check if cart exists
	var exists bool
	err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id=?)", request.CartID).Scan(&exists)
	if err != nil || !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
		return
	}

	// Retrieve items in cart
	rows, err := db.Query("SELECT item_id, count FROM cart_items WHERE cart_id=?", request.CartID)
	if err != nil {
		log.Println("Error retrieving cart items:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cart items"})
		return
	}
	defer rows.Close()

	var items []map[string]interface{}
	for rows.Next() {
		var itemID, count int
		if err := rows.Scan(&itemID, &count); err != nil {
			log.Println("Error scanning cart items:", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cart items"})
			return
		}
		items = append(items, gin.H{"item_id": itemID, "count": count})
	}

	c.JSON(http.StatusOK, gin.H{"items": items})
}