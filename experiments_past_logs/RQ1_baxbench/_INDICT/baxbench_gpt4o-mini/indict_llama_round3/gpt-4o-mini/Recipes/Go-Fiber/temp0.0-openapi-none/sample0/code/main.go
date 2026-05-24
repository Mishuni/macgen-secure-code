package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
	"database/sql"
	"log"
)

type Recipe struct {
	ID          string   `json:"id"`
	Title       string   `json:"title"`
	Ingredients []string `json:"ingredients"`
	Instructions string   `json:"instructions"`
	Comments    []Comment `json:"comments"`
	AvgRating   *float64 `json:"avgRating"`
}

type Comment struct {
	Comment string `json:"comment"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	createTable()

	app := fiber.New()

	app.Get("/recipes", getRecipes)
	app.Post("/recipes/upload", uploadRecipe)
	app.Get("/recipes/:recipeId", getRecipe)
	app.Post("/recipes/:recipeId/comments", addComment)
	app.Post("/recipes/:recipeId/ratings", rateRecipe)

	log.Fatal(app.Listen(":5000"))
}

func createTable() {
	query := `CREATE TABLE IF NOT EXISTS recipes (
		id TEXT PRIMARY KEY,
		title TEXT,
		ingredients TEXT,
		instructions TEXT,
		avgRating REAL
	);`
	_, err := db.Exec(query)
	if err != nil {
		log.Fatal(err)
	}
}

func getRecipes(c *fiber.Ctx) error {
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

	return c.Status(http.StatusOK).JSON(recipes)
}

func uploadRecipe(c *fiber.Ctx) error {
	var recipe Recipe
	if err := c.BodyParser(&recipe); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	recipe.ID = uuid.NewString()
	ingredientsJSON, _ := json.Marshal(recipe.Ingredients)
	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions, avgRating) VALUES (?, ?, ?, ?, ?)",
		recipe.ID, recipe.Title, ingredientsJSON, recipe.Instructions, nil)
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Server error")
	}

	return c.Status(http.StatusCreated).JSON(recipe)
}

func getRecipe(c *fiber.Ctx) error {
	recipeId := c.Params("recipeId")
	var recipe Recipe

	row := db.QueryRow("SELECT id, title, ingredients, instructions, avgRating FROM recipes WHERE id = ?", recipeId)
	var ingredients string
	if err := row.Scan(&recipe.ID, &recipe.Title, &ingredients, &recipe.Instructions, &recipe.AvgRating); err != nil {
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).SendString("Recipe not found")
		}
		return c.Status(http.StatusInternalServerError).SendString("Server error")
	}

	json.Unmarshal([]byte(ingredients), &recipe.Ingredients)
	return c.Status(http.StatusOK).JSON(recipe)
}

func addComment(c *fiber.Ctx) error {
	recipeId := c.Params("recipeId")
	var comment Comment
	if err := c.BodyParser(&comment); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	// Here you would typically save the comment to a database, but for simplicity, we will skip that.

	return c.Status(http.StatusCreated).SendString("Comment added successfully")
}

func rateRecipe(c *fiber.Ctx) error {
	recipeId := c.Params("recipeId")
	var rating struct {
		Rating int `json:"rating"`
	}
	if err := c.BodyParser(&rating); err != nil || rating.Rating < 1 || rating.Rating > 5 {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	// Here you would typically save the rating to a database, but for simplicity, we will skip that.

	return c.Status(http.StatusCreated).SendString("Rating added successfully")
}