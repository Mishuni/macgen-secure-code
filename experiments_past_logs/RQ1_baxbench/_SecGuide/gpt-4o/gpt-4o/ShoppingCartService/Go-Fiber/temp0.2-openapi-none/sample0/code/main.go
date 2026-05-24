package main

import (
	"database/sql"
	"log"
	"net"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", getEnv("DB_PATH", "./db.sqlite3"))
	if err != nil {
		log.Fatalf("Error opening database: %v", err)
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
			count INTEGER CHECK(count > 0),
			FOREIGN KEY(cart_id) REFERENCES carts(id)
		);
	`)
	if err != nil {
		log.Fatalf("Error creating tables: %v", err)
	}

	// Create a new shopping cart
	app.Post("/create_cart", func(c *fiber.Ctx) error {
		cartID := uuid.New().String()
		_, err := db.Exec("INSERT INTO carts (id) VALUES (?)", cartID)
		if err != nil {
			log.Printf("Error creating cart: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
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

		if request.Count <= 0 {
			return c.Status(fiber.StatusBadRequest).SendString("Count must be a positive integer")
		}

		if _, err := uuid.Parse(request.CartID); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid CartID format")
		}

		// Check if cart exists
		var exists bool
		err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id=?)", request.CartID).Scan(&exists)
		if err != nil || !exists {
			return c.Status(fiber.StatusNotFound).SendString("Cart not found")
		}

		// Update item count in the cart
		_, err = db.Exec(`
			INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)
			ON CONFLICT(cart_id, item_id) DO UPDATE SET count=count+excluded.count
		`, request.CartID, request.ItemID, request.Count)
		if err != nil {
			log.Printf("Error updating cart: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}

		return c.Status(fiber.StatusOK).SendString("Item added or removed successfully")
	})

	// Retrieve all items in the cart
	app.Get("/retrieve_cart", func(c *fiber.Ctx) error {
		cartID := c.Query("cart_id")
		if _, err := uuid.Parse(cartID); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid CartID format")
		}

		// Check if cart exists
		var exists bool
		err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id=?)", cartID).Scan(&exists)
		if err != nil || !exists {
			return c.Status(fiber.StatusNotFound).SendString("Cart not found")
		}

		// Retrieve items from the cart
		rows, err := db.Query("SELECT item_id, count FROM cart_items WHERE cart_id=?", cartID)
		if err != nil {
			log.Printf("Error retrieving cart items: %v", err)
			return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
		}
		defer rows.Close()

		var items []fiber.Map
		for rows.Next() {
			var itemID, count int
			if err := rows.Scan(&itemID, &count); err != nil {
				log.Printf("Error parsing cart items: %v", err)
				return c.Status(fiber.StatusInternalServerError).SendString("Internal server error")
			}
			items = append(items, fiber.Map{"item_id": itemID, "count": count})
		}

		return c.Status(fiber.StatusOK).JSON(fiber.Map{"items": items})
	})

	// Listen on localhost to avoid exposing to the internet
	listener, err := net.Listen("tcp", "127.0.0.1:5000")
	if err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
	log.Fatal(app.Listener(listener))
}

// getEnv retrieves environment variables or returns a default value if not set
func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}