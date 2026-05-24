
package main

import (
	"database/sql"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	r := gin.Default()

	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS carts (
		cart_id TEXT PRIMARY KEY
	);`)
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS cart_items (
		cart_id TEXT,
		item_id INTEGER,
		count INTEGER,
		PRIMARY KEY (cart_id, item_id),
		FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
	);`)
	if err != nil {
		log.Fatal(err)
	}

	r.POST("/create_cart", func(c *gin.Context) {
		cartID := uuid.New().String()
		_, err := db.Exec("INSERT INTO carts (cart_id) VALUES (?)", cartID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create cart"})
			return
		}
		c.JSON(http.StatusCreated, gin.H{"cart_id": cartID})
	})

	r.POST("/add_to_cart", func(c *gin.Context) {
		var req struct {
			CartID string `json:"cart_id" binding:"required"`
			ItemID int    `json:"item_id" binding:"required"`
			Count  int    `json:"count" binding:"required"`
		}
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		var exists bool
		err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE cart_id=?)", req.CartID).Scan(&exists)
		if err != nil || !exists {
			c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
			return
		}

		_, err = db.Exec("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count=count+excluded.count", req.CartID, req.ItemID, req.Count)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update cart"})
			return
		}
		c.JSON(http.StatusOK, gin.H{"message": "Item added or removed successfully"})
	})

	r.POST("/retrieve_cart", func(c *gin.Context) {
		var req struct {
			CartID string `json:"cart_id" binding:"required"`
		}
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		rows, err := db.Query("SELECT item_id, count FROM cart_items WHERE cart_id=?", req.CartID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cart"})
			return
		}
		defer rows.Close()

		var items []gin.H
		for rows.Next() {
			var itemID, count int
			if err := rows.Scan(&itemID, &count); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve cart"})
				return
			}
			items = append(items, gin.H{"item_id": itemID, "count": count})
		}

		if len(items) == 0 {
			c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"items": items})
	})

	r.Run("0.0.0.0:5000")
}