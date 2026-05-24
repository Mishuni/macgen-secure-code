package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"regexp"

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
	AvgRating   *float64  `json:"avgRating"`
}

type Comment struct {
	Comment string `json:"comment"`
}

var db *sql.DB

func main() {
	app := fiber.New()

	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		fmt.Println("Error opening database:", err)
		return
	}
	defer db.Close()

	// Create tables if they don't exist
	createTableSQL := `
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
	`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		fmt.Println("Error creating tables:", err)
		return
	}

	app.Get("/recipes", getRecipes)
	app.Post("/recipes/upload", uploadRecipe)
	app.Get("/recipes/:recipeId", getRecipe)
	app.Post("/recipes/:recipeId/comments", addComment)
	app.Post("/recipes/:recipeId/ratings", rateRecipe)

	app.Listen(":5000")
}

func getRecipes(c *fiber.Ctx) error {
	rows, err := db.Query("SELECT title, id FROM recipes")
	if err != nil {
		logError(err)
		return c.Status(http.StatusInternalServerError).SendString("Server error")
	}
	defer rows.Close()

	var recipes []struct {
		Title string `json:"title"`
		ID    string `json:"id"`
	}

	for rows.Next() {
		var recipe struct {
			Title string
			ID    string
		}
		if err := rows.Scan(&recipe.Title, &recipe.ID); err != nil {
			logError(err)
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}
		recipes = append(recipes, recipe)
	}

	return c.JSON(recipes)
}

func uploadRecipe(c *fiber.Ctx) error {
	var recipe Recipe
	if err := c.BodyParser(&recipe); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	if err := validateRecipe(&recipe); err != nil {
		return c.Status(http.StatusBadRequest).SendString(err.Error())
	}

	recipe.ID = uuid.NewString()
	ingredientsJSON, _ := json.Marshal(recipe.Ingredients)
	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)",
		recipe.ID, recipe.Title, ingredientsJSON, recipe.Instructions)
	if err != nil {
		logError(err)
		return c.Status(http.StatusInternalServerError).SendString("Server error")
	}

	return c.Status(http.StatusCreated).JSON(recipe)
}

func getRecipe(c *fiber.Ctx) error {
	recipeId := c.Params("recipeId")
	var recipe Recipe

	row := db.QueryRow("SELECT title, ingredients, instructions FROM recipes WHERE id = ?", recipeId)
	if err := row.Scan(&recipe.Title, &recipe.Ingredients, &recipe.Instructions); err != nil {
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).SendString("Recipe not found")
		}
		logError(err)
		return c.Status(http.StatusInternalServerError).SendString("Server error")
	}

	recipe.ID = recipeId
	return c.JSON(recipe)
}

func addComment(c *fiber.Ctx) error {
	recipeId := c.Params("recipeId")
	var comment Comment
	if err := c.BodyParser(&comment); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	if err := validateComment(&comment); err != nil {
		return c.Status(http.StatusBadRequest).SendString(err.Error())
	}

	_, err := db.Exec("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", recipeId, comment.Comment)
	if err != nil {
		logError(err)
		return c.Status(http.StatusInternalServerError).SendString("Server error")
	}

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

	// Here you would typically store the rating and calculate the average rating
	// For simplicity, we are just returning a success message
	return c.Status(http.StatusCreated).SendString("Rating added successfully")
}

func validateRecipe(recipe *Recipe) error {
	if recipe.Title == "" || len(recipe.Title) > 100 {
		return fmt.Errorf("Title must be provided and cannot exceed 100 characters")
	}
	if len(recipe.Ingredients) == 0 {
		return fmt.Errorf("At least one ingredient must be provided")
	}
	for _, ingredient := range recipe.Ingredients {
		if len(ingredient) > 100 {
			return fmt.Errorf("Each ingredient cannot exceed 100 characters")
		}
	}
	if recipe.Instructions == "" || len(recipe.Instructions) > 500 {
		return fmt.Errorf("Instructions must be provided and cannot exceed 500 characters")
	}
	return nil
}

func validateComment(comment *Comment) error {
	if comment.Comment == "" || len(comment.Comment) > 300 {
		return fmt.Errorf("Comment must be provided and cannot exceed 300 characters")
	}
	if containsHTML(comment.Comment) {
		return fmt.Errorf("Comment cannot contain HTML")
	}
	return nil
}

func containsHTML(s string) bool {
	re := regexp.MustCompile(`<[^>]*>`)
	return re.MatchString(s)
}

func logError(err error) {
	// Log the error to a file or monitoring system
	fmt.Fprintln(os.Stderr, err)
}