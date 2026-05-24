package main

import (
	"database/sql"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

const databaseFile = "db.sqlite3"

func main() {
	// Initialize the database
	db, err := sql.Open("sqlite3", databaseFile)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	// Initialize the Gin router
	router := gin.Default()

	// Routes
	router.GET("/recipes", func(c *gin.Context) {
		getRecipesHandler(c, db)
	})
	router.POST("/recipes/upload", func(c *gin.Context) {
		uploadRecipeHandler(c, db)
	})
	router.GET("/recipes/:recipeId", func(c *gin.Context) {
		getRecipeHandler(c, db)
	})
	router.POST("/recipes/:recipeId/comments", func(c *gin.Context) {
		addCommentHandler(c, db)
	})
	router.POST("/recipes/:recipeId/ratings", func(c *gin.Context) {
		addRatingHandler(c, db)
	})

	// Start the server
	log.Println("Starting server on 0.0.0.0:5000")
	if err := router.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS recipes (
			id TEXT PRIMARY KEY,
			title TEXT NOT NULL,
			ingredients TEXT NOT NULL,
			instructions TEXT NOT NULL
		);
		CREATE TABLE IF NOT EXISTS comments (
			id TEXT PRIMARY KEY,
			recipe_id TEXT NOT NULL,
			comment TEXT NOT NULL,
			FOREIGN KEY (recipe_id) REFERENCES recipes(id)
		);
		CREATE TABLE IF NOT EXISTS ratings (
			id TEXT PRIMARY KEY,
			recipe_id TEXT NOT NULL,
			rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
			FOREIGN KEY (recipe_id) REFERENCES recipes(id)
		);
	`)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}

func getRecipesHandler(c *gin.Context, db *sql.DB) {
	rows, err := db.Query("SELECT id, title FROM recipes")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve recipes"})
		return
	}
	defer rows.Close()

	var recipes []gin.H
	for rows.Next() {
		var id, title string
		if err := rows.Scan(&id, &title); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse recipes"})
			return
		}
		recipes = append(recipes, gin.H{"id": id, "title": title})
	}

	c.JSON(http.StatusOK, recipes)
}

func uploadRecipeHandler(c *gin.Context, db *sql.DB) {
	var input struct {
		Title        string   `json:"title" binding:"required"`
		Ingredients  []string `json:"ingredients" binding:"required"`
		Instructions string   `json:"instructions" binding:"required"`
	}

	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	id := uuid.New().String()
	ingredients := ""
	for i, ingredient := range input.Ingredients {
		if i > 0 {
			ingredients += ", "
		}
		ingredients += ingredient
	}

	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)",
		id, input.Title, ingredients, input.Instructions)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to upload recipe"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"id": id, "title": input.Title})
}

func getRecipeHandler(c *gin.Context, db *sql.DB) {
	recipeId := c.Param("recipeId")

	row := db.QueryRow("SELECT title, ingredients, instructions FROM recipes WHERE id = ?", recipeId)
	var title, ingredients, instructions string
	if err := row.Scan(&title, &ingredients, &instructions); err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Recipe not found"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve recipe"})
		}
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"title":        title,
		"ingredients":  ingredients,
		"instructions": instructions,
	})
}

func addCommentHandler(c *gin.Context, db *sql.DB) {
	recipeId := c.Param("recipeId")
	var input struct {
		Comment string `json:"comment" binding:"required"`
	}

	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	id := uuid.New().String()
	_, err := db.Exec("INSERT INTO comments (id, recipe_id, comment) VALUES (?, ?, ?)", id, recipeId, input.Comment)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to add comment"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"id": id, "comment": input.Comment})
}

func addRatingHandler(c *gin.Context, db *sql.DB) {
	recipeId := c.Param("recipeId")
	var input struct {
		Rating int `json:"rating" binding:"required"`
	}

	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	id := uuid.New().String()
	_, err := db.Exec("INSERT INTO ratings (id, recipe_id, rating) VALUES (?, ?, ?)", id, recipeId, input.Rating)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to add rating"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"id": id, "rating": input.Rating})
}