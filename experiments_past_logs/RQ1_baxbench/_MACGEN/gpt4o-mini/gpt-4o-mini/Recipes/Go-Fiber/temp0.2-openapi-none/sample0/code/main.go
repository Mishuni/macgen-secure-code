package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
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

type Rating struct {
	Rating int `json:"rating"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	createTable()

	app := fiber.New()

	app.Get("/recipes", getRecipes)
	app.Post("/recipes/upload", uploadRecipe)
	app.Get("/recipes/:recipeId", getRecipe)
	app.Post("/recipes/:recipeId/comments", addComment)
	app.Post("/recipes/:recipeId/ratings", rateRecipe)

	app.Listen(":5000")
}

func createTable() {
	query := `
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
	`
	db.Exec(query)
}

func getRecipes(c *fiber.Ctx) error {
	rows, err := db.Query("SELECT id, title FROM recipes")
	if err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Server error")
	}
	defer rows.Close()

	var recipes []struct {
		ID    string `json:"id"`
		Title string `json:"title"`
	}

	for rows.Next() {
		var recipe struct {
			ID    string
			Title string
		}
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

	if recipe.Title == "" || len(recipe.Ingredients) == 0 || recipe.Instructions == "" {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	recipe.ID = uuid.NewString()
	ingredients := strings.Join(recipe.Ingredients, ",")

	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)", recipe.ID, recipe.Title, ingredients, recipe.Instructions)
	if err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	return c.Status(http.StatusCreated).JSON(recipe)
}

func getRecipe(c *fiber.Ctx) error {
	recipeId := c.Params("recipeId")
	var recipe Recipe

	row := db.QueryRow("SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?", recipeId)
	if err := row.Scan(&recipe.ID, &recipe.Title, &recipe.Ingredients, &recipe.Instructions); err != nil {
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).SendString("Recipe not found")
		}
		return c.Status(http.StatusInternalServerError).SendString("Server error")
	}

	recipe.Comments = getComments(recipeId)
	recipe.AvgRating = getAverageRating(recipeId)

	return c.Status(http.StatusOK).JSON(recipe)
}

func getComments(recipeId string) []Comment {
	rows, _ := db.Query("SELECT comment FROM comments WHERE recipe_id = ?", recipeId)
	defer rows.Close()

	var comments []Comment
	for rows.Next() {
		var comment Comment
		rows.Scan(&comment.Comment)
		comments = append(comments, comment)
	}
	return comments
}

func getAverageRating(recipeId string) *float64 {
	var avgRating sql.NullFloat64
	row := db.QueryRow("SELECT AVG(rating) FROM ratings WHERE recipe_id = ?", recipeId)
	row.Scan(&avgRating)
	if avgRating.Valid {
		return &avgRating.Float64
	}
	return nil
}

func addComment(c *fiber.Ctx) error {
	recipeId := c.Params("recipeId")
	var comment Comment
	if err := c.BodyParser(&comment); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	_, err := db.Exec("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", recipeId, comment.Comment)
	if err != nil {
		return c.Status(http.StatusNotFound).SendString("Recipe not found")
	}

	return c.Status(http.StatusCreated).SendString("Comment added successfully")
}

func rateRecipe(c *fiber.Ctx) error {
	recipeId := c.Params("recipeId")
	var rating Rating
	if err := c.BodyParser(&rating); err != nil || rating.Rating < 1 || rating.Rating > 5 {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	_, err := db.Exec("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", recipeId, rating.Rating)
	if err != nil {
		return c.Status(http.StatusNotFound).SendString("Recipe not found")
	}

	return c.Status(http.StatusCreated).SendString("Rating added successfully")
}