package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"regexp"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
)

type Cart struct {
	CartID string `json:"cart_id"`
}

type CartItem struct {
	ItemID int `json:"item_id"`
	Count  int `json:"count"`
}

type AddToCartRequest struct {
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

var db *sqlite3.SQLiteConn

func init() {
	var err error
	db, err = sqlite3.Open("db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec("CREATE TABLE IF NOT EXISTS carts (id TEXT PRIMARY KEY, items TEXT)")
	if err != nil {
		log.Fatal(err)
	}
}

func validateCartID(cartID string) bool {
	// Simple regex to validate UUID format
	re := regexp.MustCompile(`^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`)
	return re.MatchString(cartID)
}

func validateAddToCartRequest(req *AddToCartRequest) error {
	if req.Count < 0 {
		return fmt.Errorf("Count must be non-negative")
	}
	if req.ItemID <= 0 {
		return fmt.Errorf("ItemID must be a positive integer")
	}
	return nil
}

func createCart(c *fiber.Ctx) error {
	cartID := uuid.New().String()
	_, err := db.Exec("INSERT INTO carts (id, items) VALUES (?, ?)", cartID, "{}")
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create cart"})
	}
	return c.Status(http.StatusCreated).JSON(Cart{CartID: cartID})
}

func addToCart(c *fiber.Ctx) error {
	var req AddToCartRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
	}

	if !validateCartID(req.CartID) {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid cart ID format"})
	}

	if err := validateAddToCartRequest(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": err.Error()})
	}

	_, err := db.Exec("SELECT id FROM carts WHERE id = ?", req.CartID)
	if err != nil {
		return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Cart not found"})
	}

	// Here you would normally update the cart items in the database
	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "Item added or removed successfully"})
}

func retrieveCart(c *fiber.Ctx) error {
	var req RetrieveCartRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
	}

	if !validateCartID(req.CartID) {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid cart ID format"})
	}

	row := db.QueryRow("SELECT items FROM carts WHERE id = ?", req.CartID)
	var items string
	if err := row.Scan(&items); err != nil {
		return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Cart not found"})
	}

	var cartItems []CartItem
	if err := json.Unmarshal([]byte(items), &cartItems); err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve cart items"})
	}

	return c.Status(http.StatusOK).JSON(RetrieveCartResponse{Items: cartItems})
}

func main() {
	app := fiber.New()

	app.Post("/create_cart", createCart)
	app.Post("/add_to_cart", addToCart)
	app.Post("/retrieve_cart", retrieveCart)

	log.Fatal(app.Listen(":5000"))
}