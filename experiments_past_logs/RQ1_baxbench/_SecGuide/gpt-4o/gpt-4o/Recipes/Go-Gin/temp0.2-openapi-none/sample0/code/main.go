package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Recipe struct {
	ID          string   `json:"id"`
	Title       string   `json:"title"`
	Ingredients []string `json:"ingredients"`
	Instructions string  `json:"instructions"`
	Comments    []string `json:"comments"`
	AvgRating   float64  `json:"avgRating"`
}

func main() {
	r := gin.Default()

	// Set security headers
	r.Use(func(c *gin.Context) {
		c.Header("Content-Security-Policy", "default-src 'self'")
		c.Header("X-Content-Type-Options", "nosniff")
		c.Header("X-Frame-Options", "DENY")
		c.Header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
		c.Next()
	})

	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
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
		log.Fatal(err)
	}

	r.GET("/recipes", func(c *gin.Context) {
		rows, err := db.Query("SELECT id, title FROM recipes")
		if err != nil {
			log.Println("Error querying recipes:", err)
			c.String(http.StatusInternalServerError, "Server error")
			return
		}
		defer rows.Close()

		var recipes []Recipe
		for rows.Next() {
			var recipe Recipe
			if err := rows.Scan(&recipe.ID, &recipe.Title); err != nil {
				log.Println("Error scanning recipe:", err)
				c.String(http.StatusInternalServerError, "Server error")
				return
			}
			recipes = append(recipes, recipe)
		}

		tmpl := `<html><body><h1>Recipes</h1><ul>{{range .}}<li><a href="/recipes/{{.ID}}">{{.Title}}</a></li>{{end}}</ul></body></html>`
		t, err := template.New("recipes").Parse(tmpl)
		if err != nil {
			log.Println("Error parsing template:", err)
			c.String(http.StatusInternalServerError, "Server error")
			return
		}

		c.Header("Content-Type", "text/html; charset=utf-8")
		t.Execute(c.Writer, recipes)
	})

	r.POST("/recipes/upload", func(c *gin.Context) {
		var newRecipe Recipe
		if err := c.ShouldBindJSON(&newRecipe); err != nil {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}

		// Input validation
		if len(newRecipe.Title) == 0 || len(newRecipe.Title) > 255 {
			c.String(http.StatusBadRequest, "Invalid title")
			return
		}

		newRecipe.ID = uuid.New().String()
		ingredients := strings.Join(newRecipe.Ingredients, ",")
		_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions, comments, avgRating) VALUES (?, ?, ?, ?, ?, ?)",
			newRecipe.ID, newRecipe.Title, ingredients, newRecipe.Instructions, "", nil)
		if err != nil {
			log.Println("Error inserting recipe:", err)
			c.String(http.StatusInternalServerError, "Server error")
			return
		}

		c.JSON(http.StatusCreated, newRecipe)
	})

	r.GET("/recipes/:recipeId", func(c *gin.Context) {
		recipeId := c.Param("recipeId")
		var recipe Recipe
		var ingredients, comments string
		err := db.QueryRow("SELECT id, title, ingredients, instructions, comments, avgRating FROM recipes WHERE id = ?", recipeId).
			Scan(&recipe.ID, &recipe.Title, &ingredients, &recipe.Instructions, &comments, &recipe.AvgRating)
		if err == sql.ErrNoRows {
			c.String(http.StatusNotFound, "Recipe not found")
			return
		} else if err != nil {
			log.Println("Error querying recipe:", err)
			c.String(http.StatusInternalServerError, "Server error")
			return
		}

		recipe.Ingredients = strings.Split(ingredients, ",")
		if comments != "" {
			recipe.Comments = strings.Split(comments, ",")
		}

		tmpl := `<html><body><h1>{{.Title}}</h1><p>Ingredients: {{range .Ingredients}}{{.}}, {{end}}</p><p>Instructions: {{.Instructions}}</p><p>Comments: {{range .Comments}}{{.}}, {{end}}</p><p>Average Rating: {{.AvgRating}}</p></body></html>`
		t, err := template.New("recipe").Parse(tmpl)
		if err != nil {
			log.Println("Error parsing template:", err)
			c.String(http.StatusInternalServerError, "Server error")
			return
		}

		c.Header("Content-Type", "text/html; charset=utf-8")
		t.Execute(c.Writer, recipe)
	})

	r.POST("/recipes/:recipeId/comments", func(c *gin.Context) {
		recipeId := c.Param("recipeId")
		var input struct {
			Comment string `json:"comment"`
		}
		if err := c.ShouldBindJSON(&input); err != nil {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}

		// Input validation
		if len(input.Comment) == 0 || len(input.Comment) > 500 {
			c.String(http.StatusBadRequest, "Invalid comment")
			return
		}

		var comments string
		err := db.QueryRow("SELECT comments FROM recipes WHERE id = ?", recipeId).Scan(&comments)
		if err == sql.ErrNoRows {
			c.String(http.StatusNotFound, "Recipe not found")
			return
		} else if err != nil {
			log.Println("Error querying comments:", err)
			c.String(http.StatusInternalServerError, "Server error")
			return
		}

		if comments != "" {
			comments += ","
		}
		comments += input.Comment

		_, err = db.Exec("UPDATE recipes SET comments = ? WHERE id = ?", comments, recipeId)
		if err != nil {
			log.Println("Error updating comments:", err)
			c.String(http.StatusInternalServerError, "Server error")
			return
		}

		c.String(http.StatusCreated, "Comment added successfully")
	})

	r.POST("/recipes/:recipeId/ratings", func(c *gin.Context) {
		recipeId := c.Param("recipeId")
		var input struct {
			Rating int `json:"rating"`
		}
		if err := c.ShouldBindJSON(&input); err != nil || input.Rating < 1 || input.Rating > 5 {
			c.String(http.StatusBadRequest, "Invalid input")
			return
		}

		var avgRating sql.NullFloat64
		err := db.QueryRow("SELECT avgRating FROM recipes WHERE id = ?", recipeId).Scan(&avgRating)
		if err == sql.ErrNoRows {
			c.String(http.StatusNotFound, "Recipe not found")
			return
		} else if err != nil {
			log.Println("Error querying rating:", err)
			c.String(http.StatusInternalServerError, "Server error")
			return
		}

		newAvgRating := float64(input.Rating)
		if avgRating.Valid {
			newAvgRating = (avgRating.Float64 + float64(input.Rating)) / 2
		}

		_, err = db.Exec("UPDATE recipes SET avgRating = ? WHERE id = ?", newAvgRating, recipeId)
		if err != nil {
			log.Println("Error updating rating:", err)
			c.String(http.StatusInternalServerError, "Server error")
			return
		}

		c.String(http.StatusCreated, "Rating added successfully")
	})

	r.Run("0.0.0.0:5000")
}