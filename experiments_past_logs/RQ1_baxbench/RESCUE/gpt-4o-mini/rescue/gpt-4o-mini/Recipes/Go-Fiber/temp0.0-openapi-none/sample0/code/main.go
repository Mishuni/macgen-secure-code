package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
)

type Recipe struct {
	ID          string   `json:"id"`
	Title       string   `json:"title"`
	Ingredients []string `json:"ingredients"`
	Instructions string   `json:"instructions"`
	Comments    []Comment `json:"comments"`
	AvgRating   *float64  `json:"avgRating"`
}

type Comment struct {
	Comment string `json:"comment"`
}

var db *sqlite3.SQLiteConn

func init() {
	var err error
	db, err = sqlite3.Open("db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	// Create tables if they don't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS recipes (
		id TEXT PRIMARY KEY,
		title TEXT,
		ingredients TEXT,
		instructions TEXT
	);`)
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS comments (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		recipe_id TEXT,
		comment TEXT,
		FOREIGN KEY(recipe_id) REFERENCES recipes(id)
	);`)
	if err != nil {
		log.Fatal(err)
	}
}

func main() {
	app := fiber.New()

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

	app.Post("/recipes/upload", func(c *fiber.Ctx) error {
		var recipe Recipe
		if err := c.BodyParser(&recipe); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		recipe.ID = uuid.NewString()
		_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)",
			recipe.ID, recipe.Title, recipe.Ingredients, recipe.Instructions)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		return c.Status(http.StatusCreated).JSON(recipe)
	})

	app.Get("/recipes/:recipeId", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")
		row := db.QueryRow("SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?", recipeId)

		var recipe Recipe
		if err := row.Scan(&recipe.ID, &recipe.Title, &recipe.Ingredients, &recipe.Instructions); err != nil {
			return c.Status(http.StatusNotFound).SendString("Recipe not found")
		}

		// Fetch comments
		commentRows, err := db.Query("SELECT comment FROM comments WHERE recipe_id = ?", recipeId)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}
		defer commentRows.Close()

		for commentRows.Next() {
			var comment Comment
			if err := commentRows.Scan(&comment.Comment); err != nil {
				return c.Status(http.StatusInternalServerError).SendString("Server error")
			}
			recipe.Comments = append(recipe.Comments, comment)
		}

		return c.JSON(recipe)
	})

	app.Post("/recipes/:recipeId/comments", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")
		var comment Comment
		if err := c.BodyParser(&comment); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		_, err := db.Exec("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", recipeId, comment.Comment)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		return c.Status(http.StatusCreated).SendString("Comment added successfully")
	})

	app.Post("/recipes/:recipeId/ratings", func(c *fiber.Ctx) error {
		// Rating functionality is not implemented in this example
		return c.Status(http.StatusNotImplemented).SendString("Rating functionality not implemented")
	})

	log.Fatal(app.Listen(":5000"))
}