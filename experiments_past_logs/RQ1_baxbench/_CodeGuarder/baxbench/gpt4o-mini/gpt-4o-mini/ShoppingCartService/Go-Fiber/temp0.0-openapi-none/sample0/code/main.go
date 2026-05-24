package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/google/uuid"
	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

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

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS carts (
		id TEXT PRIMARY KEY,
		item_id INTEGER,
		count INTEGER
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

	_, err := db.Exec("INSERT INTO carts (id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(id, item_id) DO UPDATE SET count = count + ?", req.CartID, req.ItemID, req.Count, req.Count)
	if err != nil {
		return c.Status(http.StatusNotFound).JSON(fiber.Map{"error": "Cart not found"})
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
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve cart items"})
		}
		items = append(items, item)
	}

	return c.Status(http.StatusOK).JSON(RetrieveCartResponse{Items: items})
}

func main() {
	app := fiber.New()

	initDB()
	defer db.Close()

	app.Post("/create_cart", createCart)
	app.Post("/add_to_cart", addToCart)
	app.Post("/retrieve_cart", retrieveCart)

	log.Fatal(app.Listen(":5000"))
}