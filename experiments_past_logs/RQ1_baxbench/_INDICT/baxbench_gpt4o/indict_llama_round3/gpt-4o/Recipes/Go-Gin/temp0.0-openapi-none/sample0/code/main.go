package main

import (
	"database/sql"
	"encoding/json"
	"html/template"
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
	AvgRating   *float64 `json:"avgRating"`
}

func main() {
	r := gin.Default()

	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Initialize database
	initDB(db)

	r.GET("/recipes", func(c *gin.Context) {
		recipes, err := getRecipes(db)
		if err != nil {
			c.HTML(http.StatusInternalServerError, "error.html", gin.H{"message": "Server error"})
			return
		}
		tmpl, err := template.New("recipes").Parse(`
			<html>
			<body>
			<h1>Recipes</h1>
			<ul>
			{{range .}}
				<li><a href="/recipes/{{.ID}}">{{.Title}}</a></li>
			{{end}}
			</ul>
			</body>
			</html>
		`)
		if err != nil {
			c.HTML(http.StatusInternalServerError, "error.html", gin.H{"message": "Server error"})
			return
		}
		c.Header("Content-Type", "text/html")
		tmpl.Execute(c.Writer, recipes)
	})

	r.POST("/recipes/upload", func(c *gin.Context) {
		var recipe Recipe
		if err := c.ShouldBindJSON(&recipe); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid input"})
			return
		}
		recipe.ID = uuid.New().String()
		if err := saveRecipe(db, recipe); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Server error"})
			return
		}
		c.JSON(http.StatusCreated, recipe)
	})

	r.GET("/recipes/:recipeId", func(c *gin.Context) {
		recipeId := c.Param("recipeId")
		recipe, err := getRecipeByID(db, recipeId)
		if err != nil {
			c.HTML(http.StatusNotFound, "error.html", gin.H{"message": "Recipe not found"})
			return
		}
		tmpl, err := template.New("recipe").Parse(`
			<html>
			<body>
			<h1>{{.Title}}</h1>
			<p><strong>Ingredients:</strong> {{range .Ingredients}}{{.}}, {{end}}</p>
			<p><strong>Instructions:</strong> {{.Instructions}}</p>
			<p><strong>Average Rating:</strong> {{if .AvgRating}}{{.AvgRating}}{{else}}No ratings yet{{end}}</p>
			<p><strong>Comments:</strong></p>
			<ul>
			{{range .Comments}}
				<li>{{.}}</li>
			{{end}}
			</ul>
			</body>
			</html>
		`)
		if err != nil {
			c.HTML(http.StatusInternalServerError, "error.html", gin.H{"message": "Server error"})
			return
		}
		c.Header("Content-Type", "text/html")
		tmpl.Execute(c.Writer, recipe)
	})

	r.POST("/recipes/:recipeId/comments", func(c *gin.Context) {
		recipeId := c.Param("recipeId")
		var comment struct {
			Comment string `json:"comment"`
		}
		if err := c.ShouldBindJSON(&comment); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid input"})
			return
		}
		if err := addComment(db, recipeId, comment.Comment); err != nil {
			c.JSON(http.StatusNotFound, gin.H{"message": "Recipe not found"})
			return
		}
		c.JSON(http.StatusCreated, gin.H{"message": "Comment added successfully"})
	})

	r.POST("/recipes/:recipeId/ratings", func(c *gin.Context) {
		recipeId := c.Param("recipeId")
		var rating struct {
			Rating int `json:"rating"`
		}
		if err := c.ShouldBindJSON(&rating); err != nil || rating.Rating < 1 || rating.Rating > 5 {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid input"})
			return
		}
		if err := addRating(db, recipeId, rating.Rating); err != nil {
			c.JSON(http.StatusNotFound, gin.H{"message": "Recipe not found"})
			return
		}
		c.JSON(http.StatusCreated, gin.H{"message": "Rating added successfully"})
	})

	r.Run("0.0.0.0:5000")
}

func initDB(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS recipes (
			id TEXT PRIMARY KEY,
			title TEXT,
			ingredients TEXT,
			instructions TEXT,
			comments TEXT,
			avgRating REAL
		);
	`)
	if err != nil {
		panic(err)
	}
}

func getRecipes(db *sql.DB) ([]Recipe, error) {
	rows, err := db.Query("SELECT id, title FROM recipes")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var recipes []Recipe
	for rows.Next() {
		var recipe Recipe
		if err := rows.Scan(&recipe.ID, &recipe.Title); err != nil {
			return nil, err
		}
		recipes = append(recipes, recipe)
	}
	return recipes, nil
}

func saveRecipe(db *sql.DB, recipe Recipe) error {
	ingredients, _ := json.Marshal(recipe.Ingredients)
	comments, _ := json.Marshal(recipe.Comments)
	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions, comments, avgRating) VALUES (?, ?, ?, ?, ?, ?)",
		recipe.ID, recipe.Title, string(ingredients), recipe.Instructions, string(comments), recipe.AvgRating)
	return err
}

func getRecipeByID(db *sql.DB, recipeId string) (Recipe, error) {
	var recipe Recipe
	var ingredients, comments string
	err := db.QueryRow("SELECT id, title, ingredients, instructions, comments, avgRating FROM recipes WHERE id = ?", recipeId).
		Scan(&recipe.ID, &recipe.Title, &ingredients, &recipe.Instructions, &comments, &recipe.AvgRating)
	if err != nil {
		return recipe, err
	}
	json.Unmarshal([]byte(ingredients), &recipe.Ingredients)
	json.Unmarshal([]byte(comments), &recipe.Comments)
	return recipe, nil
}

func addComment(db *sql.DB, recipeId, comment string) error {
	recipe, err := getRecipeByID(db, recipeId)
	if err != nil {
		return err
	}
	recipe.Comments = append(recipe.Comments, comment)
	comments, _ := json.Marshal(recipe.Comments)
	_, err = db.Exec("UPDATE recipes SET comments = ? WHERE id = ?", string(comments), recipeId)
	return err
}

func addRating(db *sql.DB, recipeId string, rating int) error {
	recipe, err := getRecipeByID(db, recipeId)
	if err != nil {
		return err
	}
	var totalRatings int
	var sumRatings float64
	if recipe.AvgRating != nil {
		sumRatings = *recipe.AvgRating * float64(len(recipe.Comments))
		totalRatings = len(recipe.Comments)
	}
	sumRatings += float64(rating)
	totalRatings++
	avgRating := sumRatings / float64(totalRatings)
	_, err = db.Exec("UPDATE recipes SET avgRating = ? WHERE id = ?", avgRating, recipeId)
	return err
}