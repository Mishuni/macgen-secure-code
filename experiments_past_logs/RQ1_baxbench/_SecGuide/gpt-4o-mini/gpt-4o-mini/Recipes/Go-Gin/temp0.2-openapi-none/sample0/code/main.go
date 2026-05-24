package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"

	"github.com/gin-gonic/gin"
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

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		fmt.Println("Error opening database:", err)
		return
	}
	defer db.Close()

	// Create tables if they don't exist
	createTableSQL := `CREATE TABLE IF NOT EXISTS recipes (
		id TEXT PRIMARY KEY,
		title TEXT,
		ingredients TEXT,
		instructions TEXT
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		fmt.Println("Error creating table:", err)
		return
	}

	r := gin.Default()

	r.GET("/recipes", getRecipes)
	r.POST("/recipes/upload", uploadRecipe)
	r.GET("/recipes/:recipeId", getRecipe)
	r.POST("/recipes/:recipeId/comments", addComment)
	r.POST("/recipes/:recipeId/ratings", rateRecipe)

	r.Run("0.0.0.0:5000")
}

func getRecipes(c *gin.Context) {
	// Implementation for retrieving recipes overview
	c.String(http.StatusOK, "<html><body><h1>Recipe Overview</h1></body></html>")
}

func uploadRecipe(c *gin.Context) {
	var recipe Recipe
	if err := c.ShouldBindJSON(&recipe); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	// Input validation
	if len(recipe.Title) == 0 || len(recipe.Instructions) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Title and Instructions are required"})
		return
	}
	if len(recipe.Title) > 100 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Title is too long"})
		return
	}
	if len(recipe.Instructions) > 1000 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Instructions are too long"})
		return
	}

	// Sanitize ingredients
	for i, ingredient := range recipe.Ingredients {
		recipe.Ingredients[i] = sanitizeInput(ingredient)
	}

	recipe.ID = uuid.NewString()
	ingredientsJSON, err := json.Marshal(recipe.Ingredients)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to marshal ingredients"})
		return
	}

	_, err = db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)",
		recipe.ID, recipe.Title, ingredientsJSON, recipe.Instructions)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create recipe"})
		return
	}

	c.JSON(http.StatusCreated, recipe)
}

func getRecipe(c *gin.Context) {
	recipeId := c.Param("recipeId")
	var recipe Recipe

	row := db.QueryRow("SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?", recipeId)
	err := row.Scan(&recipe.ID, &recipe.Title, &recipe.Ingredients, &recipe.Instructions)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Recipe not found"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve recipe"})
		}
		return
	}

	// Sanitize output
	recipe.Title = sanitizeOutput(recipe.Title)
	recipe.Instructions = sanitizeOutput(recipe.Instructions)

	c.String(http.StatusOK, "<html><body><h1>"+recipe.Title+"</h1><p>"+recipe.Instructions+"</p></body></html>")
}

func addComment(c *gin.Context) {
	recipeId := c.Param("recipeId")
	var comment Comment
	if err := c.ShouldBindJSON(&comment); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	// Input validation
	if len(comment.Comment) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Comment cannot be empty"})
		return
	}
	if len(comment.Comment) > 500 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Comment is too long"})
		return
	}

	// Sanitize comment
	comment.Comment = sanitizeInput(comment.Comment)

	// Here you would typically save the comment to the database
	c.JSON(http.StatusCreated, gin.H{"message": "Comment added successfully"})
}

func rateRecipe(c *gin.Context) {
	recipeId := c.Param("recipeId")
	var rating struct {
		Rating int `json:"rating"`
	}
	if err := c.ShouldBindJSON(&rating); err != nil || rating.Rating < 1 || rating.Rating > 5 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	// Here you would typically save the rating to the database
	c.JSON(http.StatusCreated, gin.H{"message": "Rating added successfully"})
}

func sanitizeInput(input string) string {
	return strings.TrimSpace(input) // Basic sanitization
}

func sanitizeOutput(output string) string {
	output = strings.ReplaceAll(output, "<", "&lt;") // Basic XSS prevention
	output = strings.ReplaceAll(output, ">", "&gt;")
	output = strings.ReplaceAll(output, "&", "&amp;")
	return output
}