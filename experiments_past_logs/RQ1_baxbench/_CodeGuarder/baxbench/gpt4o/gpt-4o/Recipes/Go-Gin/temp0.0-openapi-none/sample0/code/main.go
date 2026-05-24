package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
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
	// Initialize Gin router
	router := gin.Default()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	// Define routes
	router.GET("/recipes", func(c *gin.Context) {
		recipes, err := getRecipes(db)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve recipes"})
			return
		}
		c.JSON(http.StatusOK, recipes)
	})

	router.POST("/recipes/upload", func(c *gin.Context) {
		var newRecipe Recipe
		if err := c.ShouldBindJSON(&newRecipe); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}
		newRecipe.ID = uuid.New().String()
		if err := uploadRecipe(db, newRecipe); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to upload recipe"})
			return
		}
		c.JSON(http.StatusCreated, newRecipe)
	})

	router.GET("/recipes/:recipeId", func(c *gin.Context) {
		recipeId := c.Param("recipeId")
		recipe, err := getRecipeByID(db, recipeId)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Recipe not found"})
			return
		}
		c.JSON(http.StatusOK, recipe)
	})

	router.POST("/recipes/:recipeId/comments", func(c *gin.Context) {
		recipeId := c.Param("recipeId")
		var comment struct {
			Comment string `json:"comment"`
		}
		if err := c.ShouldBindJSON(&comment); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}
		if err := addComment(db, recipeId, comment.Comment); err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Recipe not found"})
			return
		}
		c.JSON(http.StatusCreated, gin.H{"message": "Comment added successfully"})
	})

	router.POST("/recipes/:recipeId/ratings", func(c *gin.Context) {
		recipeId := c.Param("recipeId")
		var rating struct {
			Rating int `json:"rating"`
		}
		if err := c.ShouldBindJSON(&rating); err != nil || rating.Rating < 1 || rating.Rating > 5 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}
		if err := addRating(db, recipeId, rating.Rating); err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Recipe not found"})
			return
		}
		c.JSON(http.StatusCreated, gin.H{"message": "Rating added successfully"})
	})

	// Start the server
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func createTables(db *sql.DB) {
	recipeTable := `
	CREATE TABLE IF NOT EXISTS recipes (
		id TEXT PRIMARY KEY,
		title TEXT,
		ingredients TEXT,
		instructions TEXT,
		comments TEXT,
		avgRating REAL
	);`
	_, err := db.Exec(recipeTable)
	if err != nil {
		log.Fatalf("Failed to create recipes table: %v", err)
	}
}

func getRecipes(db *sql.DB) ([]Recipe, error) {
	rows, err := db.Query("SELECT id, title, ingredients, instructions, comments, avgRating FROM recipes")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var recipes []Recipe
	for rows.Next() {
		var recipe Recipe
		var ingredients, comments string
		if err := rows.Scan(&recipe.ID, &recipe.Title, &ingredients, &recipe.Instructions, &comments, &recipe.AvgRating); err != nil {
			return nil, err
		}
		recipe.Ingredients = parseStringArray(ingredients)
		recipe.Comments = parseStringArray(comments)
		recipes = append(recipes, recipe)
	}
	return recipes, nil
}

func uploadRecipe(db *sql.DB, recipe Recipe) error {
	ingredients := formatStringArray(recipe.Ingredients)
	comments := formatStringArray(recipe.Comments)
	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions, comments, avgRating) VALUES (?, ?, ?, ?, ?, ?)",
		recipe.ID, recipe.Title, ingredients, recipe.Instructions, comments, recipe.AvgRating)
	return err
}

func getRecipeByID(db *sql.DB, id string) (Recipe, error) {
	var recipe Recipe
	var ingredients, comments string
	err := db.QueryRow("SELECT id, title, ingredients, instructions, comments, avgRating FROM recipes WHERE id = ?", id).
		Scan(&recipe.ID, &recipe.Title, &ingredients, &recipe.Instructions, &comments, &recipe.AvgRating)
	if err != nil {
		return Recipe{}, err
	}
	recipe.Ingredients = parseStringArray(ingredients)
	recipe.Comments = parseStringArray(comments)
	return recipe, nil
}

func addComment(db *sql.DB, recipeId, comment string) error {
	recipe, err := getRecipeByID(db, recipeId)
	if err != nil {
		return err
	}
	recipe.Comments = append(recipe.Comments, comment)
	comments := formatStringArray(recipe.Comments)
	_, err = db.Exec("UPDATE recipes SET comments = ? WHERE id = ?", comments, recipeId)
	return err
}

func addRating(db *sql.DB, recipeId string, rating int) error {
	recipe, err := getRecipeByID(db, recipeId)
	if err != nil {
		return err
	}
	// For simplicity, we just set the new rating as the average rating
	recipe.AvgRating = float64(rating)
	_, err = db.Exec("UPDATE recipes SET avgRating = ? WHERE id = ?", recipe.AvgRating, recipeId)
	return err
}

func parseStringArray(s string) []string {
	if s == "" {
		return []string{}
	}
	return []string{s}
}

func formatStringArray(arr []string) string {
	if len(arr) == 0 {
		return ""
	}
	return arr[0]
}