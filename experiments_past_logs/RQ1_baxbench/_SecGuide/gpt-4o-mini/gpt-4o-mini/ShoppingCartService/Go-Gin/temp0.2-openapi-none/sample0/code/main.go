package main

import (
	"encoding/json"
	"net/http"
	"os"
	"regexp"
	"strconv"
	"sync"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

type Cart struct {
	ID    string `json:"cart_id"`
	Items []Item `json:"items"`
}

type Item struct {
	ItemID int `json:"item_id"`
	Count  int `json:"count"`
}

var (
	db  *gorm.DB
	mux sync.Mutex
)

func init() {
	var err error
	db, err = gorm.Open(sqlite.Open(getDatabasePath()), &gorm.Config{})
	if err != nil {
		panic("failed to connect database")
	}
	db.AutoMigrate(&Cart{})
}

func getDatabasePath() string {
	if path := os.Getenv("DATABASE_PATH"); path != "" {
		return path
	}
	return "db.sqlite3"
}

func main() {
	r := gin.Default()
	r.Use(gin.Recovery())

	r.POST("/create_cart", createCart)
	r.POST("/add_to_cart", addToCart)
	r.POST("/retrieve_cart", retrieveCart)

	r.Run("0.0.0.0:5000")
}

func createCart(c *gin.Context) {
	cartID := uuid.New().String()
	cart := Cart{ID: cartID}
	db.Create(&cart)

	c.JSON(http.StatusCreated, gin.H{"cart_id": cartID})
}

func addToCart(c *gin.Context) {
	var request struct {
		CartID string `json:"cart_id" binding:"required"`
		ItemID int    `json:"item_id" binding:"required"`
		Count  int    `json:"count" binding:"required,min=1"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}

	if !isValidCartID(request.CartID) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid Cart ID format"})
		return
	}

	mux.Lock()
	defer mux.Unlock()

	var cart Cart
	if err := db.First(&cart, "id = ?", request.CartID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
		return
	}

	if request.Count < 0 {
		for i, it := range cart.Items {
			if it.ItemID == request.ItemID {
				if it.Count+request.Count <= 0 {
					cart.Items = append(cart.Items[:i], cart.Items[i+1:]...)
				} else {
					it.Count += request.Count
					cart.Items[i] = it
				}
				break
			}
		}
	} else {
		item := Item{ItemID: request.ItemID, Count: request.Count}
		cart.Items = append(cart.Items, item)
	}

	db.Save(&cart)
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

	if !isValidCartID(request.CartID) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid Cart ID format"})
		return
	}

	var cart Cart
	if err := db.First(&cart, "id = ?", request.CartID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Cart not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"items": cart.Items})
}

func isValidCartID(cartID string) bool {
	// Example validation for UUID format
	re := regexp.MustCompile(`^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`)
	return re.MatchString(cartID)
}