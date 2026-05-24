package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Recipe struct {
	ID          string   `json:"id"`
	Title       string   `json:"title"`
	Ingredients []string `json:"ingredients"`
	Instructions string  `json:"instructions"`
	Comments    []Comment `json:"comments"`
	AvgRating   *float64 `json:"avgRating"`
}

type Comment struct {
	Comment string `json:"comment"`
}

type Rating struct {
	Rating int `json:"rating"`
}

func main() {
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS recipes (
		id TEXT PRIMARY KEY,
		title TEXT,
		ingredients TEXT,
		instructions TEXT
	);`)
	if err != nil {
		panic(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS comments (
		id TEXT PRIMARY KEY,
		recipe_id TEXT,
		comment TEXT,
		FOREIGN KEY(recipe_id) REFERENCES recipes(id)
	);`)
	if err != nil {
		panic(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS ratings (
		id TEXT PRIMARY KEY,
		recipe_id TEXT,
		rating INTEGER,
		FOREIGN KEY(recipe_id) REFERENCES recipes(id)
	);`)
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
	})

	r.POST("/recipes/upload", func(c *gin.Context) {
		var recipe Recipe
		if err := c.ShouldBindJSON(&recipe); err != nil {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}

		recipe.ID = uuid.New().String()
		ingredients, _ := json.Marshal(recipe.Ingredients)

		_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)",
			recipe.ID, recipe.Title, string(ingredients), recipe.Instructions)
		if err != nil {
			c.String(http.StatusInternalServerError, "Server error")
			return
		}

		c.JSON(http.StatusCreated, recipe)
	})

	r.GET("/recipes/:recipeId", func(c *gin.Context) {
		recipeId := c.Param("recipeId")

		if !isValidUUID(recipeId) {
			c.String(http.StatusBadRequest, "Invalid recipe ID format")
			return
		}

		var recipe Recipe
		var ingredients string
		err := db.QueryRow("SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?", recipeId).
			Scan(&recipe.ID, &recipe.Title, &ingredients, &recipe.Instructions)
		if err == sql.ErrNoRows {
			c.String(http.StatusNotFound, "Recipe not found")
			return
		} else if err != nil {
			c.String(http.StatusInternalServerError, "Server error")
			return
		}

		json.Unmarshal([]byte(ingredients), &recipe.Ingredients)

		rows, err := db.Query("SELECT comment FROM comments WHERE recipe_id = ?", recipeId)
		if err != nil {
			c.String(http.StatusInternalServerError, "Server error")
			return
		}
		defer rows.Close()

		for rows.Next() {
			var comment Comment
			if err := rows.Scan(&comment.Comment); err != nil {
				c.String(http.StatusInternalServerError, "Server error")
				return
			}
			recipe.Comments = append(recipe.Comments, comment)
		}

		var totalRating int
		var ratingCount int
		ratingRows, err := db.Query("SELECT rating FROM ratings WHERE recipe_id = ?", recipeId)
		if err != nil {
			c.String(http.StatusInternalServerError, "Server error")
			return
		}
		defer ratingRows.Close()

		for ratingRows.Next() {
			var rating int
			if err := ratingRows.Scan(&rating); err != nil {
				c.String(http.StatusInternalServerError, "Server error")
				return
			}
			totalRating += rating
			ratingCount++
		}

		if ratingCount > 0 {
			avgRating := float64(totalRating) / float64(ratingCount)
			recipe.AvgRating = &avgRating
		}

		c.HTML(http.StatusOK, "recipe.html", gin.H{"recipe": recipe})
	})

	r.POST("/recipes/:recipeId/comments", func(c *gin.Context) {
		recipeId := c.Param("recipeId")

		if !isValidUUID(recipeId) {
			c.String(http.StatusBadRequest, "Invalid recipe ID format")
			return
		}

		var comment Comment
		if err := c.ShouldBindJSON(&comment); err != nil {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}

		_, err := db.Exec("INSERT INTO comments (id, recipe_id, comment) VALUES (?, ?, ?)",
			uuid.New().String(), recipeId, comment.Comment)
		if err != nil {
			c.String(http.StatusInternalServerError, "Server error")
			return
		}

		c.String(http.StatusCreated, "Comment added successfully")
	})

	r.POST("/recipes/:recipeId/ratings", func(c *gin.Context) {
		recipeId := c.Param("recipeId")

		if !isValidUUID(recipeId) {
			c.String(http.StatusBadRequest, "Invalid recipe ID format")
			return
		}

		var rating Rating
		if err := c.ShouldBindJSON(&rating); err != nil {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}

		if rating.Rating < 1 || rating.Rating > 5 {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}

		_, err := db.Exec("INSERT INTO ratings (id, recipe_id, rating) VALUES (?, ?, ?)",
			uuid.New().String(), recipeId, rating.Rating)
		if err != nil {
			c.String(http.StatusInternalServerError, "Server error")
			return
		}

		c.String(http.StatusCreated, "Rating added successfully")
	})

	r.Run("0.0.0.0:5000")
}

func isValidUUID(u string) bool {
	r := regexp.MustCompile(`^[a-fA-F0-9-]{36}$`)
	return r.MatchString(u)
}