package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"html"
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

	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "db.sqlite3"
	}

	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS recipes (
		id TEXT PRIMARY KEY,
		title TEXT,
		ingredients TEXT,
		instructions TEXT,
		comments TEXT,
		avgRating REAL
	)`)
	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	app.Get("/recipes", func(c *fiber.Ctx) error {
		rows, err := db.Query("SELECT id, title FROM recipes")
		if err != nil {
			log.Printf("Database query error: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}
		defer rows.Close()

		var recipes []string
		for rows.Next() {
			var id, title string
			if err := rows.Scan(&id, &title); err != nil {
				log.Printf("Row scan error: %v", err)
				return c.Status(http.StatusInternalServerError).SendString("Internal server error")
			}
			recipes = append(recipes, fmt.Sprintf("<a href=\"/recipes/%s\">%s</a>", html.EscapeString(id), html.EscapeString(title)))
		}

		return c.SendString(strings.Join(recipes, "<br>"))
	})

	app.Post("/recipes/upload", func(c *fiber.Ctx) error {
		var recipe Recipe
		if err := c.BodyParser(&recipe); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		if !validateRecipe(recipe) {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		recipe.ID = uuid.New().String()
		recipe.Comments = []string{}
		recipe.AvgRating = nil

		ingredientsJSON, err := json.Marshal(recipe.Ingredients)
		if err != nil {
			log.Printf("JSON marshal error: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}

		_, err = db.Exec("INSERT INTO recipes (id, title, ingredients, instructions, comments, avgRating) VALUES (?, ?, ?, ?, ?, ?)",
			recipe.ID, recipe.Title, string(ingredientsJSON), recipe.Instructions, "[]", nil)
		if err != nil {
			log.Printf("Database insert error: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}

		return c.Status(http.StatusCreated).JSON(recipe)
	})

	app.Get("/recipes/:recipeId", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")
		row := db.QueryRow("SELECT id, title, ingredients, instructions, comments, avgRating FROM recipes WHERE id = ?", recipeId)

		var recipe Recipe
		var ingredientsJSON, commentsJSON string
		if err := row.Scan(&recipe.ID, &recipe.Title, &ingredientsJSON, &recipe.Instructions, &commentsJSON, &recipe.AvgRating); err != nil {
			if err == sql.ErrNoRows {
				return c.Status(http.StatusNotFound).SendString("Recipe not found")
			}
			log.Printf("Row scan error: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}

		if err := json.Unmarshal([]byte(ingredientsJSON), &recipe.Ingredients); err != nil {
			log.Printf("JSON unmarshal error: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}

		if err := json.Unmarshal([]byte(commentsJSON), &recipe.Comments); err != nil {
			log.Printf("JSON unmarshal error: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}

		return c.JSON(recipe)
	})

	app.Post("/recipes/:recipeId/comments", func(c *fiber.Ctx) error {
		recipeId := c.Params("recipeId")
		var input struct {
			Comment string `json:"comment"`
		}
		if err := c.BodyParser(&input); err != nil {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		if !validateComment(input.Comment) {
			return c.Status(http.StatusBadRequest).SendString("Invalid input")
		}

		row := db.QueryRow("SELECT comments FROM recipes WHERE id = ?", recipeId)
		var commentsJSON string
		if err := row.Scan(&commentsJSON); err != nil {
			if err == sql.ErrNoRows {
				return c.Status(http.StatusNotFound).SendString("Recipe not found")
			}
			log.Printf("Row scan error: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}

		var comments []string
		if err := json.Unmarshal([]byte(commentsJSON), &comments); err != nil {
			log.Printf("JSON unmarshal error: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}

		comments = append(comments, input.Comment)
		updatedCommentsJSON, err := json.Marshal(comments)
		if err != nil {
			log.Printf("JSON marshal error: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}

		_, err = db.Exec("UPDATE recipes SET comments = ? WHERE id = ?", string(updatedCommentsJSON), recipeId)
		if err != nil {
			log.Printf("Database update error: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
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

		tx, err := db.Begin()
		if err != nil {
			log.Printf("Transaction begin error: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}
		defer tx.Rollback()

		row := tx.QueryRow("SELECT avgRating FROM recipes WHERE id = ?", recipeId)
		var avgRating sql.NullFloat64
		if err := row.Scan(&avgRating); err != nil {
			if err == sql.ErrNoRows {
				return c.Status(http.StatusNotFound).SendString("Recipe not found")
			}
			log.Printf("Row scan error: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}

		newAvgRating := float64(input.Rating)
		if avgRating.Valid {
			newAvgRating = (avgRating.Float64 + float64(input.Rating)) / 2
		}

		_, err = tx.Exec("UPDATE recipes SET avgRating = ? WHERE id = ?", newAvgRating, recipeId)
		if err != nil {
			log.Printf("Database update error: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}

		if err := tx.Commit(); err != nil {
			log.Printf("Transaction commit error: %v", err)
			return c.Status(http.StatusInternalServerError).SendString("Internal server error")
		}

		return c.Status(http.StatusCreated).SendString("Rating added successfully")
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func validateRecipe(recipe Recipe) bool {
	if recipe.Title == "" || len(recipe.Ingredients) == 0 || recipe.Instructions == "" {
		return false
	}
	return true
}

func validateComment(comment string) bool {
	if comment == "" {
		return false
	}
	return true
}