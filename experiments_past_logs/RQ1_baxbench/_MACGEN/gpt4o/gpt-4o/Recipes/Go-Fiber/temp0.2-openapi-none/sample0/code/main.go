package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Recipe struct {
	ID          string   `json:"id"`
	Title       string   `json:"title"`
	Ingredients []string `json:"ingredients"`
	Instructions string  `json:"instructions"`
	Comments    []string `json:"comments"`
	AvgRating   *float64 `json:"avgRating"`
}

func main() {
	app := fiber.New()

	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	createTables(db)

	app.Get("/recipes", func(c *fiber.Ctx) error {
		rows, err := db.Query("SELECT id, title FROM recipes")
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Server error")
		}
		defer rows.Close()

		var recipes []Recipe
		for rows.Next() {
			var recipe Recipe
			if err := rows.Scan(&recipe.ID, &recipe.Title); err != nil {
				return c.Status(fiber.StatusInternalServerError).SendString("Server error")
			}
			recipes = append(recipes, recipe)
		}

		return c.JSON(recipes)
	})

	app.Post("/recipes/upload", func(c *fiber.Ctx) error {
		var recipe Recipe
		if err := c.BodyParser(&recipe); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		recipe.ID = uuid.New().String()
		ingredients := strings.Join(recipe.Ingredients, ",")
		_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)",
			recipe.ID, recipe.Title, ingredients, recipe.Instructions)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Server error")
		}

		return c.Status(fiber.StatusCreated).JSON(recipe)
	})

	app.Get("/recipes/:recipeId", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")
		row := db.QueryRow("SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?", recipeId)

		var recipe Recipe
		var ingredients string
		if err := row.Scan(&recipe.ID, &recipe.Title, &ingredients, &recipe.Instructions); err != nil {
			if err == sql.ErrNoRows {
				return c.Status(fiber.StatusNotFound).SendString("Recipe not found")
			}
			return c.Status(fiber.StatusInternalServerError).SendString("Server error")
		}
		recipe.Ingredients = strings.Split(ingredients, ",")

		return c.JSON(recipe)
	})

	app.Post("/recipes/:recipeId/comments", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")
		var input struct {
			Comment string `json:"comment"`
		}
		if err := c.BodyParser(&input); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		_, err := db.Exec("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", recipeId, input.Comment)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Server error")
		}

		return c.Status(fiber.StatusCreated).SendString("Comment added successfully")
	})

	app.Post("/recipes/:recipeId/ratings", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")
		var input struct {
			Rating int `json:"rating"`
		}
		if err := c.BodyParser(&input); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		if input.Rating < 1 || input.Rating > 5 {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid input")
		}

		_, err := db.Exec("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", recipeId, input.Rating)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).SendString("Server error")
		}

		return c.Status(fiber.StatusCreated).SendString("Rating added successfully")
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS recipes (
			id TEXT PRIMARY KEY,
			title TEXT,
			ingredients TEXT,
			instructions TEXT
		);
		CREATE TABLE IF NOT EXISTS comments (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			recipe_id TEXT,
			comment TEXT,
			FOREIGN KEY(recipe_id) REFERENCES recipes(id)
		);
		CREATE TABLE IF NOT EXISTS ratings (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			recipe_id TEXT,
			rating INTEGER,
			FOREIGN KEY(recipe_id) REFERENCES recipes(id)
		);
	`)
	if err != nil {
		log.Fatal(err)
	}
}