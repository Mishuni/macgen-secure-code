
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
	app := fiber.New()

	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS carts (
			id TEXT PRIMARY KEY
		);
		CREATE TABLE IF NOT EXISTS cart_items (
			cart_id TEXT,
			item_id INTEGER,
			count INTEGER,
			FOREIGN KEY(cart_id) REFERENCES carts(id)
		);
	`)
	if err != nil {
		log.Fatal(err)
	}

	app.Post("/create_cart", func(c *fiber.Ctx) error {
		cartID := uuid.New().String()
		_, err := db.Exec("INSERT INTO carts (id) VALUES (?)", cartID)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to create cart")
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
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		if _, err := uuid.Parse(request.CartID); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid cart ID")
		}

		var exists bool
		err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM carts WHERE id=?)", request.CartID).Scan(&exists)
		if err != nil || !exists {
			return c.Status(fiber.StatusNotFound).SendString("Cart not found")
		}

		_, err = db.Exec(`
			INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)
			ON CONFLICT(cart_id, item_id) DO UPDATE SET count=count+excluded.count
		`, request.CartID, request.ItemID, request.Count)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to update cart")
		}

		return c.Status(fiber.StatusOK).SendString("Item added or removed successfully")
	})

	app.Post("/retrieve_cart", func(c *fiber.Ctx) error {
		var request struct {
			CartID string `json:"cart_id"`
		}
		if err := c.BodyParser(&request); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid request")
		}

		if _, err := uuid.Parse(request.CartID); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid cart ID")
		}

		rows, err := db.Query("SELECT item_id, count FROM cart_items WHERE cart_id=?", request.CartID)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Failed to retrieve cart")
		}
		defer rows.Close()

		items := []fiber.Map{}
		for rows.Next() {
			var itemID, count int
			if err := rows.Scan(&itemID, &count); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Failed to parse cart items")
			}
			items = append(items, fiber.Map{"item_id": itemID, "count": count})
		}

		if len(items) == 0 {
			return c.Status(fiber.StatusNotFound).SendString("Cart not found")
		}

		return c.Status(fiber.StatusOK).JSON(fiber.Map{"items": items})
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}