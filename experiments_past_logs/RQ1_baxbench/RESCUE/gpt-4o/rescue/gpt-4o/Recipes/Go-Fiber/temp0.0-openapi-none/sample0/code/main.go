package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"

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
	app.Get("/recipes", func(c *fiber.Ctx) error {
		rows, err := db.Query("SELECT id, title FROM recipes")
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to fetch recipes")
		}
		defer rows.Close()

		var recipes []map[string]string
		for rows.Next() {
			var id, title string
			if err := rows.Scan(&id, &title); err != nil {
				return c.Status(http.StatusInternalServerError).SendString("Failed to parse recipes")
			}
			recipes = append(recipes, map[string]string{"id": id, "title": title})
		}

		return c.JSON(recipes)
	})

	app.Post("/recipes/upload", func(c *fiber.Ctx) error {
		var body struct {
			Title       string   `json:"title"`
			Ingredients []string `json:"ingredients"`
			Instructions string   `json:"instructions"`
		}

		if err := c.BodyParser(&body); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		// Validate input
		if strings.TrimSpace(body.Title) == "" || len(body.Ingredients) == 0 || strings.TrimSpace(body.Instructions) == "" {
			return c.Status(http.StatusBadRequest).SendString("Missing required fields")
		}

		// Insert recipe into database
		id := uuid.New().String()
		ingredients := strings.Join(body.Ingredients, ", ")
		_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)", id, body.Title, ingredients, body.Instructions)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to save recipe")
		}

		return c.Status(http.StatusCreated).JSON(map[string]string{"id": id, "title": body.Title})
	})

	app.Get("/recipes/:recipeId", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")
		row := db.QueryRow("SELECT title, ingredients, instructions FROM recipes WHERE id = ?", recipeId)

		var title, ingredients, instructions string
		if err := row.Scan(&title, &ingredients, &instructions); err != nil {
			if err == sql.ErrNoRows {
				return c.Status(http.StatusNotFound).SendString("Recipe not found")
			}
			return c.Status(http.StatusInternalServerError).SendString("Failed to fetch recipe")
		}

		return c.JSON(map[string]interface{}{
			"title":        title,
			"ingredients":  strings.Split(ingredients, ", "),
			"instructions": instructions,
		})
	})

	app.Post("/recipes/:recipeId/comments", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")
		var body struct {
			Comment string `json:"comment"`
		}

		if err := c.BodyParser(&body); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		if strings.TrimSpace(body.Comment) == "" {
			return c.Status(http.StatusBadRequest).SendString("Comment cannot be empty")
		}

		_, err := db.Exec("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", recipeId, body.Comment)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to save comment")
		}

		return c.Status(http.StatusCreated).SendString("Comment added successfully")
	})

	app.Post("/recipes/:recipeId/ratings", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")
		var body struct {
			Rating int `json:"rating"`
		}

		if err := c.BodyParser(&body); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		if body.Rating < 1 || body.Rating > 5 {
			return c.Status(http.StatusBadRequest).SendString("Rating must be between 1 and 5")
		}

		_, err := db.Exec("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", recipeId, body.Rating)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Failed to save rating")
		}

		return c.Status(http.StatusCreated).SendString("Rating added successfully")
	})

	// Start server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS recipes (
			id TEXT PRIMARY KEY,
			title TEXT NOT NULL,
			ingredients TEXT NOT NULL,
			instructions TEXT NOT NULL
		);
		CREATE TABLE IF NOT EXISTS comments (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			recipe_id TEXT NOT NULL,
			comment TEXT NOT NULL,
			FOREIGN KEY (recipe_id) REFERENCES recipes (id)
		);
		CREATE TABLE IF NOT EXISTS ratings (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			recipe_id TEXT NOT NULL,
			rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
			FOREIGN KEY (recipe_id) REFERENCES recipes (id)
		);
	`)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}