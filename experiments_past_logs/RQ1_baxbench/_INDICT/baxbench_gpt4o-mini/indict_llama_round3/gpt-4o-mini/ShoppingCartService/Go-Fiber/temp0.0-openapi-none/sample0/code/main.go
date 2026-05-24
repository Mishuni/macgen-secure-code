package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Cart struct {
	CartID string `json:"cart_id"`
}

type AddToCartRequest struct {
	CartID string `json:"cart_id"`
	ItemID int    `json:"item_id"`
	Count  int    `json:"count"`
}

type RetrieveCartRequest struct {
	CartID string `json:"cart_id"`
}

type CartItem struct {
	ItemID int `json:"item_id"`
	Count  int `json:"count"`
}

type RetrieveCartResponse struct {
	Items []CartItem `json:"items"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS carts (
		id TEXT NOT NULL,
		item_id INTEGER NOT NULL,
		count INTEGER NOT NULL,
		PRIMARY KEY (id, item_id)
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func createCart(c *fiber.Ctx) error {
	cartID := uuid.New().String()
	_, err := db.Exec("INSERT INTO carts (id) VALUES (?)", cartID)
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

	if req.Count == 0 {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Count must be non-zero"})
	}

	// Check if cart exists
	var exists int
	err := db.QueryRow("SELECT COUNT(*) FROM carts WHERE id = ?", req.CartID).Scan(&exists)
	if err != nil || exists == 0 {
		return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Cart not found"})
	}

	if req.Count < 0 {
		_, err := db.Exec("DELETE FROM carts WHERE id = ? AND item_id = ?", req.CartID, req.ItemID)
		if err != nil {
			return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Item not found in cart"})
		}
	} else {
		_, err := db.Exec("INSERT INTO carts (id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(id, item_id) DO UPDATE SET count = count + ?", req.CartID, req.ItemID, req.Count, req.Count)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to add item to cart"})
		}
	}
	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "Item added or removed successfully"})
}

func retrieveCart(c *fiber.Ctx) error {
	var req RetrieveCartRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
	}

	rows, err := db.Query("SELECT item_id, count FROM carts WHERE id = ?", req.CartID)
	if err != nil {
		return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Cart not found"})
	}
	defer rows.Close()

	var items []CartItem
	for rows.Next() {
		var item CartItem
		if err := rows.Scan(&item.ItemID, &item.Count); err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve items"})
		}
		items = append(items, item)
	}

	return c.Status(http.StatusOK).JSON(RetrieveCartResponse{Items: items})
}

func main() {
	app := fiber.New()

	app.Post("/create_cart", createCart)
	app.Post("/add_to_cart", addToCart)
	app.Post("/retrieve_cart", retrieveCart)

	log.Fatal(app.Listen(":5000"))
}