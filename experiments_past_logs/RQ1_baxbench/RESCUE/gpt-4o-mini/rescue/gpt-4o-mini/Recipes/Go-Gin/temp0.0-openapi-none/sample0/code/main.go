package main

import (
	"encoding/json"
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"database/sql"
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

	// Create the recipes table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS recipes (
		id TEXT PRIMARY KEY,
		title TEXT,
		ingredients TEXT,
		instructions TEXT
	)`)
	if err != nil {
		panic(err)
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
	rows, err := db.Query("SELECT id, title FROM recipes")
	if err != nil {
		c.String(http.StatusInternalServerError, "Server error")
		return
	}
	defer rows.Close()

	var recipes []Recipe
	for rows.Next() {
		var recipe Recipe
		if err := rows.Scan(&recipe.ID, &recipe.Title); err != nil {
			c.String(http.StatusInternalServerError, "Server error")
			return
		}
		recipes = append(recipes, recipe)
	}

	c.HTML(http.StatusOK, "recipes.html", gin.H{"recipes": recipes})
}

func uploadRecipe(c *gin.Context) {
	var recipe Recipe
	if err := c.ShouldBindJSON(&recipe); err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	recipe.ID = uuid.NewString()
	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)",
		recipe.ID, recipe.Title, json.Marshal(recipe.Ingredients), recipe.Instructions)
	if err != nil {
		c.String(http.StatusInternalServerError, "Server error")
		return
	}

	c.JSON(http.StatusCreated, recipe)
}

func getRecipe(c *gin.Context) {
	recipeId := c.Param("recipeId")
	row := db.QueryRow("SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?", recipeId)

	var recipe Recipe
	var ingredients string
	if err := row.Scan(&recipe.ID, &recipe.Title, &ingredients, &recipe.Instructions); err != nil {
		if err == sql.ErrNoRows {
			c.String(http.StatusNotFound, "Recipe not found")
			return
		}
		c.String(http.StatusInternalServerError, "Server error")
		return
	}

	json.Unmarshal([]byte(ingredients), &recipe.Ingredients)
	c.HTML(http.StatusOK, "recipe.html", recipe)
}

func addComment(c *gin.Context) {
	recipeId := c.Param("recipeId")
	var comment Comment
	if err := c.ShouldBindJSON(&comment); err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	// Here you would typically save the comment to the database
	// For simplicity, we are not implementing this part

	c.String(http.StatusCreated, "Comment added successfully")
}

func rateRecipe(c *gin.Context) {
	recipeId := c.Param("recipeId")
	var rating Rating
	if err := c.ShouldBindJSON(&rating); err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	// Here you would typically save the rating to the database
	// For simplicity, we are not implementing this part

	c.String(http.StatusCreated, "Rating added successfully")
}