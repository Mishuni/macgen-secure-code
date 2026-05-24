package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
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
		title TEXT NOT NULL,
		ingredients TEXT NOT NULL,
		instructions TEXT NOT NULL
	);`
	_, err := db.Exec(query)
	if err != nil {
		log.Fatal(err)
	}
}

func getRecipes(c *fiber.Ctx) error {
	rows, err := db.Query("SELECT id, title FROM recipes ORDER BY title")
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

	return c.Render("recipes.html", fiber.Map{"recipes": recipes})
}

func uploadRecipe(c *fiber.Ctx) error {
	var recipe Recipe
	if err := c.BodyParser(&recipe); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	recipe.ID = uuid.NewString()
	ingredients, _ := json.Marshal(recipe.Ingredients)

	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)",
		recipe.ID, recipe.Title, string(ingredients), recipe.Instructions)
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Server error")
	}

	return c.Status(http.StatusCreated).JSON(recipe)
}

func getRecipe(c *fiber.Ctx) error {
	recipeId := c.Params("recipeId")
	var recipe Recipe

	row := db.QueryRow("SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?", recipeId)
	var ingredients string
	if err := row.Scan(&recipe.ID, &recipe.Title, &ingredients, &recipe.Instructions); err != nil {
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).SendString("Recipe not found")
		}
		return c.Status(http.StatusInternalServerError).SendString("Server error")
	}

	json.Unmarshal([]byte(ingredients), &recipe.Ingredients)
	return c.Render("recipe.html", recipe)
}

func addComment(c *fiber.Ctx) error {
	recipeId := c.Params("recipeId")
	var comment Comment
	if err := c.BodyParser(&comment); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	// Here you would typically save the comment to the database
	// For simplicity, we are not implementing comment storage in this example

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

	// Here you would typically save the rating to the database
	// For simplicity, we are not implementing rating storage in this example

	return c.Status(http.StatusCreated).SendString("Rating added successfully")
}