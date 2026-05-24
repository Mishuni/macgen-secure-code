package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
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

	_, err = db.Exec(`
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

		html := "<h1>Recipes</h1><ul>"
		for _, recipe := range recipes {
			html += fmt.Sprintf("<li><a href=\"/recipes/%s\">%s</a></li>", recipe.ID, recipe.Title)
		}
		html += "</ul>"

		return c.Type("html").SendString(html)
	})

	app.Post("/recipes/upload", func(c *fiber.Ctx) error {
		var recipe Recipe
		if err := c.BodyParser(&recipe); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		if len(recipe.Title) == 0 || len(recipe.Ingredients) == 0 || len(recipe.Instructions) == 0 {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		recipe.ID = uuid.New().String()
		ingredients, err := json.Marshal(recipe.Ingredients)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		_, err = db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)",
			recipe.ID, recipe.Title, string(ingredients), recipe.Instructions)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		return c.Status(http.StatusCreated).JSON(recipe)
	})

	app.Get("/recipes/:recipeId", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")

		var recipe Recipe
		var ingredients string
		err := db.QueryRow("SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?", recipeId).
			Scan(&recipe.ID, &recipe.Title, &ingredients, &recipe.Instructions)
		if err == sql.ErrNoRows {
			return c.Status(http.StatusNotFound).SendString("Recipe not found")
		} else if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		if err := json.Unmarshal([]byte(ingredients), &recipe.Ingredients); err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		rows, err := db.Query("SELECT comment FROM comments WHERE recipe_id = ?", recipeId)
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
		err = db.QueryRow("SELECT SUM(rating), COUNT(rating) FROM ratings WHERE recipe_id = ?", recipeId).
			Scan(&totalRating, &ratingCount)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		if ratingCount > 0 {
			avgRating := float64(totalRating) / float64(ratingCount)
			recipe.AvgRating = &avgRating
		}

		html := fmt.Sprintf("<h1>%s</h1><p>%s</p><h2>Ingredients</h2><ul>", recipe.Title, recipe.Instructions)
		for _, ingredient := range recipe.Ingredients {
			html += fmt.Sprintf("<li>%s</li>", ingredient)
		}
		html += "</ul><h2>Comments</h2><ul>"
		for _, comment := range recipe.Comments {
			html += fmt.Sprintf("<li>%s</li>", comment)
		}
		html += "</ul>"
		if recipe.AvgRating != nil {
			html += fmt.Sprintf("<h2>Average Rating: %.2f</h2>", *recipe.AvgRating)
		} else {
			html += "<h2>No Ratings Yet</h2>"
		}

		return c.Type("html").SendString(html)
	})

	app.Post("/recipes/:recipeId/comments", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")

		var input struct {
			Comment string `json:"comment"`
		}
		if err := c.BodyParser(&input); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		if len(strings.TrimSpace(input.Comment)) == 0 {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		_, err := db.Exec("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", recipeId, input.Comment)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		return c.Status(http.StatusCreated).SendString("Comment added successfully")
	})

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

		_, err := db.Exec("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", recipeId, input.Rating)
		if err != nil {
			return c.Status(http.StatusInternalServerError).SendString("Server error")
		}

		return c.Status(http.StatusCreated).SendString("Rating added successfully")
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}