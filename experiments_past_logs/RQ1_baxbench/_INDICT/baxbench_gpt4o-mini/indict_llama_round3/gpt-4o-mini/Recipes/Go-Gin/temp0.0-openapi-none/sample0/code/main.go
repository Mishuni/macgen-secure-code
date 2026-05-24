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
	ID          string    `json:"id"`
	Title       string    `json:"title"`
	Ingredients []string  `json:"ingredients"`
	Instructions string    `json:"instructions"`
	Comments    []Comment `json:"comments"`
	AvgRating   *float64  `json:"avgRating"`
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
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables
	createTableSQL := `CREATE TABLE IF NOT EXISTS recipes (
		id TEXT PRIMARY KEY,
		title TEXT,
		ingredients TEXT,
		instructions TEXT
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}

	createCommentsTableSQL := `CREATE TABLE IF NOT EXISTS comments (
		id TEXT PRIMARY KEY,
		recipe_id TEXT,
		comment TEXT,
		FOREIGN KEY(recipe_id) REFERENCES recipes(id)
	);`
	_, err = db.Exec(createCommentsTableSQL)
	if err != nil {
		panic(err)
	}

	createRatingsTableSQL := `CREATE TABLE IF NOT EXISTS ratings (
		id TEXT PRIMARY KEY,
		recipe_id TEXT,
		rating INTEGER CHECK(rating >= 1 AND rating <= 5),
		FOREIGN KEY(recipe_id) REFERENCES recipes(id)
	);`
	_, err = db.Exec(createRatingsTableSQL)
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
			c.String(http.StatusInternalServerError, "Server error")
			return
		}
		recipes = append(recipes, recipe)
	}

	c.JSON(http.StatusOK, recipes)
}

func uploadRecipe(c *gin.Context) {
	var recipe Recipe
	if err := c.ShouldBindJSON(&recipe); err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	recipe.ID = uuid.NewString()
	ingredients, _ := json.Marshal(recipe.Ingredients)

	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)",
		recipe.ID, recipe.Title, string(ingredients), recipe.Instructions)
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
		c.String(http.StatusNotFound, "Recipe not found")
		return
	}

	json.Unmarshal([]byte(ingredients), &recipe.Ingredients)

	// Fetch comments
	commentRows, err := db.Query("SELECT comment FROM comments WHERE recipe_id = ?", recipeId)
	if err != nil {
		c.String(http.StatusInternalServerError, "Server error")
		return
	}
	defer commentRows.Close()

	for commentRows.Next() {
		var comment Comment
		if err := commentRows.Scan(&comment.Comment); err != nil {
			c.String(http.StatusInternalServerError, "Server error")
			return
		}
		recipe.Comments = append(recipe.Comments, comment)
	}

	// Fetch ratings
	ratingRows, err := db.Query("SELECT rating FROM ratings WHERE recipe_id = ?", recipeId)
	if err != nil {
		c.String(http.StatusInternalServerError, "Server error")
		return
	}
	defer ratingRows.Close()

	var totalRating int
	var count int
	for ratingRows.Next() {
		var rating Rating
		if err := ratingRows.Scan(&rating.Rating); err != nil {
			c.String(http.StatusInternalServerError, "Server error")
			return
		}
		totalRating += rating.Rating
		count++
	}

	if count > 0 {
		avgRating := float64(totalRating) / float64(count)
		recipe.AvgRating = &avgRating
	} else {
		recipe.AvgRating = nil
	}

	c.JSON(http.StatusOK, recipe)
}

func addComment(c *gin.Context) {
	recipeId := c.Param("recipeId")
	var comment Comment
	if err := c.ShouldBindJSON(&comment); err != nil {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	commentID := uuid.NewString()
	_, err := db.Exec("INSERT INTO comments (id, recipe_id, comment) VALUES (?, ?, ?)", commentID, recipeId, comment.Comment)
	if err != nil {
		c.String(http.StatusInternalServerError, "Server error")
		return
	}

	c.String(http.StatusCreated, "Comment added successfully")
}

func rateRecipe(c *gin.Context) {
	recipeId := c.Param("recipeId")
	var rating Rating
	if err := c.ShouldBindJSON(&rating); err != nil || rating.Rating < 1 || rating.Rating > 5 {
		c.String(http.StatusBadRequest, "Invalid input")
		return
	}

	ratingID := uuid.NewString()
	_, err := db.Exec("INSERT INTO ratings (id, recipe_id, rating) VALUES (?, ?, ?)", ratingID, recipeId, rating.Rating)
	if err != nil {
		c.String(http.StatusInternalServerError, "Server error")
		return
	}

	c.String(http.StatusCreated, "Rating added successfully")
}