package main

import (
	"database/sql"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Fiber app
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	// Routes
	app.Post("/create_cart", func(c *fiber.Ctx) error {
		cartID := uuid.New().String()

		_, err := db.Exec("INSERT INTO carts (id) VALUES (?)", cartID)
		if err != nil {
			log.Printf("Failed to create cart: %v", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create cart"})
		}

		return c.Status(fiber.StatusCreated).JSON(fiber.Map{"cart_id": cartID})
	})

	app.Post("/add_to_cart", func(c *fiber.Ctx) error {
		var request struct {
			CartID string `json:"cart_id"`
			ItemID int    `json:"item_id"`
			Count  int    `json:"count"`
		}

		if err := c.BodyParser(&request); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request body"})
		}

		// Check if cart exists
		var exists bool
		err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id = ?)", request.CartID).Scan(&exists)
		if err != nil || !exists {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Cart not found"})
		}

		// Update or insert item in the cart
		_, err = db.Exec(`
			INSERT INTO cart_items (cart_id, item_id, count)
			VALUES (?, ?, ?)
			ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + excluded.count
		`, request.CartID, request.ItemID, request.Count)
		if err != nil {
			log.Printf("Failed to update cart: %v", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to update cart"})
		}

		// Remove item if count is zero or less
		_, err = db.Exec("DELETE FROM cart_items WHERE cart_id = ? AND item_id = ? AND count <= 0", request.CartID, request.ItemID)
		if err != nil {
			log.Printf("Failed to clean up cart items: %v", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to clean up cart items"})
		}

		return c.Status(fiber.StatusOK).JSON(fiber.Map{"message": "Item added or removed successfully"})
	})

	app.Post("/retrieve_cart", func(c *fiber.Ctx) error {
		var request struct {
			CartID string `json:"cart_id"`
		}

		if err := c.BodyParser(&request); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request body"})
		}

		// Check if cart exists
		var exists bool
		err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id = ?)", request.CartID).Scan(&exists)
		if err != nil || !exists {
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Cart not found"})
		}

		// Retrieve items in the cart
		rows, err := db.Query("SELECT item_id, count FROM cart_items WHERE cart_id = ?", request.CartID)
		if err != nil {
			log.Printf("Failed to retrieve cart items: %v", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve cart items"})
		}
		defer rows.Close()

		items := []map[string]interface{}{}
		for rows.Next() {
			var itemID, count int
			if err := rows.Scan(&itemID, &count); err != nil {
				log.Printf("Failed to scan cart item: %v", err)
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to retrieve cart items"})
			}
			items = append(items, fiber.Map{"item_id": itemID, "count": count})
		}

		return c.Status(fiber.StatusOK).JSON(fiber.Map{"items": items})
	})

	// Start server
	log.Fatal(app.Listen("0.0.0.0:5000"))
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
			FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE
		);
	`)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}