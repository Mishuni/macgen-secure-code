package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
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
		panic(err)
	}
	defer db.Close()

	createTable()

	router := gin.Default()
	router.GET("/recipes", getRecipes)
	router.POST("/recipes/upload", uploadRecipe)
	router.GET("/recipes/:recipeId", getRecipeByID)
	router.POST("/recipes/:recipeId/comments", addComment)
	router.POST("/recipes/:recipeId/ratings", rateRecipe)

	router.Run("0.0.0.0:5000")
}

func createTable() {
	createTableSQL := `CREATE TABLE IF NOT EXISTS recipes (
		id TEXT PRIMARY KEY,
		title TEXT NOT NULL,
		ingredients TEXT NOT NULL,
		instructions TEXT NOT NULL,
		avgRating REAL
	);`
	_, err := db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}

	createCommentsTableSQL := `CREATE TABLE IF NOT EXISTS comments (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		recipeId TEXT,
		comment TEXT,
		FOREIGN KEY(recipeId) REFERENCES recipes(id)
	);`
	_, err = db.Exec(createCommentsTableSQL)
	if err != nil {
		panic(err)
	}
}

func getRecipes(c *gin.Context) {
	rows, err := db.Query("SELECT id, title FROM recipes ORDER BY avgRating DESC")
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
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	recipe.ID = uuid.New().String()
	ingredientsJSON, _ := json.Marshal(recipe.Ingredients)

	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)",
		recipe.ID, recipe.Title, string(ingredientsJSON), recipe.Instructions)
	if err != nil {
		c.String(http.StatusInternalServerError, "Server error")
		return
	}

	c.JSON(http.StatusCreated, recipe)
}

func getRecipeByID(c *gin.Context) {
	recipeId := c.Param("recipeId")
	var recipe Recipe

	row := db.QueryRow("SELECT id, title, ingredients, instructions, avgRating FROM recipes WHERE id = ?", recipeId)
	var ingredientsJSON string
	if err := row.Scan(&recipe.ID, &recipe.Title, &ingredientsJSON, &recipe.Instructions, &recipe.AvgRating); err != nil {
		if err == sql.ErrNoRows {
			c.String(http.StatusNotFound, "Recipe not found")
			return
		}
		c.String(http.StatusInternalServerError, "Server error")
		return
	}

	json.Unmarshal([]byte(ingredientsJSON), &recipe.Ingredients)

	comments, err := getComments(recipeId)
	if err != nil {
		c.String(http.StatusInternalServerError, "Server error")
		return
	}
	recipe.Comments = comments

	c.HTML(http.StatusOK, "recipe.html", recipe)
}

func getComments(recipeId string) ([]Comment, error) {
	rows, err := db.Query("SELECT comment FROM comments WHERE recipeId = ?", recipeId)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var comments []Comment
	for rows.Next() {
		var comment Comment
		if err := rows.Scan(&comment.Comment); err != nil {
			return nil, err
		}
		comments = append(comments, comment)
	}
	return comments, nil
}

func addComment(c *gin.Context) {
	recipeId := c.Param("recipeId")
	var comment Comment
	if err := c.ShouldBindJSON(&comment); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	_, err := db.Exec("INSERT INTO comments (recipeId, comment) VALUES (?, ?)", recipeId, comment.Comment)
	if err != nil {
		c.String(http.StatusInternalServerError, "Server error")
		return
	}

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

	var avgRating float64
	err := db.QueryRow("SELECT avgRating FROM recipes WHERE id = ?", recipeId).Scan(&avgRating)
	if err != nil {
		if err == sql.ErrNoRows {
			c.String(http.StatusNotFound, "Recipe not found")
			return
		}
		c.String(http.StatusInternalServerError, "Server error")
		return
	}

	newAvgRating := (avgRating + float64(rating.Rating)) / 2
	_, err = db.Exec("UPDATE recipes SET avgRating = ? WHERE id = ?", newAvgRating, recipeId)
	if err != nil {
		c.String(http.StatusInternalServerError, "Server error")
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Rating added successfully"})
}