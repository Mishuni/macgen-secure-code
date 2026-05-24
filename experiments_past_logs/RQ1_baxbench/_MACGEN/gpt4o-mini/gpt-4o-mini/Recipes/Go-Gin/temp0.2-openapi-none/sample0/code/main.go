package main

import (
	"database/sql"
	"encoding/json"
	"net/http"

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

func main() {
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

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
	CREATE TABLE IF NOT EXISTS ratings (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		recipe_id TEXT,
		rating INTEGER,
		FOREIGN KEY(recipe_id) REFERENCES recipes(id)
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		panic(err)
	}

	r := gin.Default()

	r.GET("/recipes", func(c *gin.Context) {
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

		c.HTML(http.StatusOK, "recipes.html", gin.H{"recipes": recipes})
	})

	r.POST("/recipes/upload", func(c *gin.Context) {
		var recipe Recipe
		if err := c.ShouldBindJSON(&recipe); err != nil || recipe.Title == "" || len(recipe.Ingredients) == 0 || recipe.Instructions == "" {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}
		recipe.ID = uuid.NewString()
		ingredientsJSON, _ := json.Marshal(recipe.Ingredients)
		_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)", recipe.ID, recipe.Title, ingredientsJSON, recipe.Instructions)
		if err != nil {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}
		c.JSON(http.StatusCreated, recipe)
	})

	r.GET("/recipes/:recipeId", func(c *gin.Context) {
		recipeId := c.Param("recipeId")
		if recipeId == "" {
			c.String(http.StatusBadRequest, "Invalid recipe ID")
			return
		}
		var recipe Recipe
		row := db.QueryRow("SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?", recipeId)
		if err := row.Scan(&recipe.ID, &recipe.Title, &recipe.Ingredients, &recipe.Instructions); err != nil {
			c.String(http.StatusNotFound, "Recipe not found")
			return
		}

		rows, _ := db.Query("SELECT comment FROM comments WHERE recipe_id = ?", recipeId)
		defer rows.Close()
		for rows.Next() {
			var comment Comment
			if err := rows.Scan(&comment.Comment); err == nil {
				recipe.Comments = append(recipe.Comments, comment)
			}
		}

		var avgRating sql.NullFloat64
		row = db.QueryRow("SELECT AVG(rating) FROM ratings WHERE recipe_id = ?", recipeId)
		row.Scan(&avgRating)
		if avgRating.Valid {
			recipe.AvgRating = &avgRating.Float64
		}

		c.HTML(http.StatusOK, "recipe.html", gin.H{"recipe": recipe})
	})

	r.POST("/recipes/:recipeId/comments", func(c *gin.Context) {
		recipeId := c.Param("recipeId")
		if recipeId == "" {
			c.String(http.StatusBadRequest, "Invalid recipe ID")
			return
		}
		var comment Comment
		if err := c.ShouldBindJSON(&comment); err != nil || comment.Comment == "" {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}
		_, err := db.Exec("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", recipeId, comment.Comment)
		if err != nil {
			c.String(http.StatusNotFound, "Recipe not found")
			return
		}
		c.String(http.StatusCreated, "Comment added successfully")
	})

	r.POST("/recipes/:recipeId/ratings", func(c *gin.Context) {
		recipeId := c.Param("recipeId")
		if recipeId == "" {
			c.String(http.StatusBadRequest, "Invalid recipe ID")
			return
		}
		var rating struct {
			Rating int `json:"rating"`
		}
		if err := c.ShouldBindJSON(&rating); err != nil || rating.Rating < 1 || rating.Rating > 5 {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}
		_, err := db.Exec("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", recipeId, rating.Rating)
		if err != nil {
			c.String(http.StatusNotFound, "Recipe not found")
			return
		}
		c.String(http.StatusCreated, "Rating added successfully")
	})

	r.Run("0.0.0.0:5000")
}