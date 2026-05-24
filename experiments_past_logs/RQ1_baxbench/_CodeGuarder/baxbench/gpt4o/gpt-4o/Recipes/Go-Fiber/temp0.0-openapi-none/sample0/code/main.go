package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"strconv"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Recipe struct {
	ID           string   `json:"id"`
	Title        string   `json:"title"`
	Ingredients  []string `json:"ingredients"`
	Instructions string   `json:"instructions"`
	Comments     []string `json:"comments"`
	AvgRating    float64  `json:"avgRating"`
}

func main() {
	app := fiber.New()

	// Initialize database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create tables if not exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS recipes (
			id TEXT PRIMARY KEY,
			title TEXT NOT NULL,
			instructions TEXT NOT NULL
		);
		CREATE TABLE IF NOT EXISTS ingredients (
			id TEXT,
			ingredient TEXT,
			FOREIGN KEY(id) REFERENCES recipes(id)
		);
		CREATE TABLE IF NOT EXISTS comments (
			id TEXT,
			comment TEXT,
			FOREIGN KEY(id) REFERENCES recipes(id)
		);
		CREATE TABLE IF NOT EXISTS ratings (
			id TEXT,
			rating INTEGER,
			FOREIGN KEY(id) REFERENCES recipes(id)
		);
	`)
	if err != nil {
		log.Fatal(err)
	}

	// Get recipes overview
	app.Get("/recipes", func(c *fiber.Ctx) error {
		rows, err := db.Query("SELECT id, title FROM recipes")
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}
		defer rows.Close()

		var recipes []Recipe
		for rows.Next() {
			var recipe Recipe
			if err := rows.Scan(&recipe.ID, &recipe.Title); err != nil {
				return c.Status(http.StatusInternalServerError).SendString("Server error")
			}
			recipes = append(recipes, recipe)
		}

		return c.JSON(recipes)
	})

	// Upload a new recipe
	app.Post("/recipes/upload", func(c *fiber.Ctx) error {
		var recipe Recipe
		if err := c.BodyParser(&recipe); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		recipe.ID = uuid.New().String()

		tx, err := db.Begin()
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		_, err = tx.Exec("INSERT INTO recipes (id, title, instructions) VALUES (?, ?, ?)", recipe.ID, recipe.Title, recipe.Instructions)
		if err != nil {
			tx.Rollback()
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		for _, ingredient := range recipe.Ingredients {
			_, err = tx.Exec("INSERT INTO ingredients (id, ingredient) VALUES (?, ?)", recipe.ID, ingredient)
			if err != nil {
				tx.Rollback()
				return c.Status(http.StatusInternalServerError).SendString("Server error")
			}
		}

		if err := tx.Commit(); err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		return c.Status(http.StatusCreated).JSON(recipe)
	})

	// Get a recipe by ID
	app.Get("/recipes/:recipeId", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")

		var recipe Recipe
		err := db.QueryRow("SELECT id, title, instructions FROM recipes WHERE id = ?", recipeId).Scan(&recipe.ID, &recipe.Title, &recipe.Instructions)
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).SendString("Recipe not found")
		} else if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		rows, err := db.Query("SELECT ingredient FROM ingredients WHERE id = ?", recipeId)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}
		defer rows.Close()

		for rows.Next() {
			var ingredient string
			if err := rows.Scan(&ingredient); err != nil {
				return c.Status(http.StatusInternalServerError).SendString("Server error")
			}
			recipe.Ingredients = append(recipe.Ingredients, ingredient)
		}

		rows, err = db.Query("SELECT comment FROM comments WHERE id = ?", recipeId)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}
		defer rows.Close()

		for rows.Next() {
			var comment string
			if err := rows.Scan(&comment); err != nil {
				return c.Status(http.StatusInternalServerError).SendString("Server error")
			}
			recipe.Comments = append(recipe.Comments, comment)
		}

		var totalRating int
		var ratingCount int
		err = db.QueryRow("SELECT SUM(rating), COUNT(rating) FROM ratings WHERE id = ?", recipeId).Scan(&totalRating, &ratingCount)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		if ratingCount > 0 {
			recipe.AvgRating = float64(totalRating) / float64(ratingCount)
		} else {
			recipe.AvgRating = 0
		}

		return c.JSON(recipe)
	})

	// Add a comment to a recipe
	app.Post("/recipes/:recipeId/comments", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")

		var input struct {
			Comment string `json:"comment"`
		}
		if err := c.BodyParser(&input); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		_, err := db.Exec("INSERT INTO comments (id, comment) VALUES (?, ?)", recipeId, input.Comment)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		return c.Status(http.StatusCreated).SendString("Comment added successfully")
	})

	// Rate a recipe
	app.Post("/recipes/:recipeId/ratings", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")

		var input struct {
			Rating int `json:"rating"`
		}
		if err := c.BodyParser(&input); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		if input.Rating < 1 || input.Rating > 5 {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		_, err := db.Exec("INSERT INTO ratings (id, rating) VALUES (?, ?)", recipeId, input.Rating)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		return c.Status(http.StatusCreated).SendString("Rating added successfully")
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}