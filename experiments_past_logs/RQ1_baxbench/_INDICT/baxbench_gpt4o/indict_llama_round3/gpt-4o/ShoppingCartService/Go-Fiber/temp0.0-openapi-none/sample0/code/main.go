package main

import (
	"database/sql"
	"log"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create tables if they don't exist
	_, err = db.Exec(`
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
		log.Fatal(err)
	}

	// Create a new shopping cart
	app.Post("/create_cart", func(c *fiber.Ctx) error {
		cartID := uuid.New().String()
		_, err := db.Exec("INSERT INTO carts (id) VALUES (?)", cartID)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to create cart")
		}
		return c.Status(fiber.StatusCreated).JSON(fiber.Map{"cart_id": cartID})
	})

	// Add or remove items from the cart
	app.Post("/add_to_cart", func(c *fiber.Ctx) error {
		var request struct {
			CartID string `json:"cart_id"`
			ItemID int    `json:"item_id"`
			Count  int    `json:"count"`
		}
		if err := c.BodyParser(&request); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		// Check if cart exists
		var exists bool
		err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id=?)", request.CartID).Scan(&exists)
		if err != nil || !exists {
			return c.Status(fiber.StatusNotFound).SendString("Cart not found")
		}

		// Check if item already exists in the cart
		var currentCount int
		err = db.QueryRow("SELECT count FROM cart_items WHERE cart_id=? AND item_id=?", request.CartID, request.ItemID).Scan(&currentCount)
		if err != nil && err != sql.ErrNoRows {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to update cart")
		}

		newCount := currentCount + request.Count
		if newCount < 0 {
			return c.Status(fiber.StatusBadRequest).SendString("Item count cannot be negative")
		}

		if newCount == 0 {
			_, err = db.Exec("DELETE FROM cart_items WHERE cart_id=? AND item_id=?", request.CartID, request.ItemID)
		} else {
			_, err = db.Exec(`
				INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)
				ON CONFLICT(cart_id, item_id) DO UPDATE SET count=excluded.count
			`, request.CartID, request.ItemID, newCount)
		}

		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to update cart")
		}

		return c.Status(fiber.StatusOK).SendString("Item added or removed successfully")
	})

	// Retrieve all items in the cart
	app.Post("/retrieve_cart", func(c *fiber.Ctx) error {
		var request struct {
			CartID string `json:"cart_id"`
		}
		if err := c.BodyParser(&request); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		// Check if cart exists
		var exists bool
		err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id=?)", request.CartID).Scan(&exists)
		if err != nil || !exists {
			return c.Status(fiber.StatusNotFound).SendString("Cart not found")
		}

		// Retrieve items from the cart
		rows, err := db.Query("SELECT item_id, count FROM cart_items WHERE cart_id=?", request.CartID)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to retrieve cart items")
		}
		defer rows.Close()

		var items []fiber.Map
		for rows.Next() {
			var itemID, count int
			if err := rows.Scan(&itemID, &count); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Failed to parse cart items")
			}
			items = append(items, fiber.Map{"item_id": itemID, "count": count})
		}

		return c.Status(fiber.StatusOK).JSON(fiber.Map{"items": items})
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}