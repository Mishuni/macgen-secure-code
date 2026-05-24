package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func initDatabase() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Create tables
	_, err = db.Exec(`
	CREATE TABLE IF NOT EXISTS recipes (
		id TEXT PRIMARY KEY,
		title TEXT NOT NULL,
		ingredients TEXT NOT NULL,
		instructions TEXT NOT NULL,
		avg_rating REAL
	);
	CREATE TABLE IF NOT EXISTS comments (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		recipe_id TEXT NOT NULL,
		comment TEXT NOT NULL,
		FOREIGN KEY(recipe_id) REFERENCES recipes(id)
	);
	CREATE TABLE IF NOT EXISTS ratings (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		recipe_id TEXT NOT NULL,
		rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
		FOREIGN KEY(recipe_id) REFERENCES recipes(id)
	);
	`)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}

func getRecipesHandler(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query("SELECT id, title FROM recipes")
	if err != nil {
		http.Error(w, "Failed to fetch recipes", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var recipes []map[string]string
	for rows.Next() {
		var id, title string
		if err := rows.Scan(&id, &title); err != nil {
			http.Error(w, "Failed to parse recipes", http.StatusInternalServerError)
			return
		}
		recipes = append(recipes, map[string]string{"id": id, "title": title})
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(recipes)
}

func uploadRecipeHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
		return
	}

	var recipe struct {
		Title        string   `json:"title"`
		Ingredients  []string `json:"ingredients"`
		Instructions string   `json:"instructions"`
	}

	if err := json.NewDecoder(r.Body).Decode(&recipe); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if recipe.Title == "" || len(recipe.Ingredients) == 0 || recipe.Instructions == "" {
		http.Error(w, "Missing required fields", http.StatusBadRequest)
		return
	}

	recipeID := uuid.New().String()
	ingredientsJSON, _ := json.Marshal(recipe.Ingredients)

	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)",
		recipeID, recipe.Title, string(ingredientsJSON), recipe.Instructions)
	if err != nil {
		http.Error(w, "Failed to save recipe", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"id": recipeID})
}

func getRecipeHandler(w http.ResponseWriter, r *http.Request) {
	recipeID := r.URL.Query().Get("recipeId")
	if recipeID == "" {
		http.Error(w, "Missing recipe ID", http.StatusBadRequest)
		return
	}

	row := db.QueryRow("SELECT title, ingredients, instructions, avg_rating FROM recipes WHERE id = ?", recipeID)
	var title, ingredients, instructions string
	var avgRating sql.NullFloat64
	if err := row.Scan(&title, &ingredients, &instructions, &avgRating); err != nil {
		http.Error(w, "Recipe not found", http.StatusNotFound)
		return
	}

	var comments []string
	commentRows, err := db.Query("SELECT comment FROM comments WHERE recipe_id = ?", recipeID)
	if err != nil {
		http.Error(w, "Failed to fetch comments", http.StatusInternalServerError)
		return
	}
	defer commentRows.Close()

	for commentRows.Next() {
		var comment string
		if err := commentRows.Scan(&comment); err != nil {
			http.Error(w, "Failed to parse comments", http.StatusInternalServerError)
			return
		}
		comments = append(comments, comment)
	}

	response := map[string]interface{}{
		"title":        title,
		"ingredients":  ingredients,
		"instructions": instructions,
		"avgRating":    avgRating.Float64,
		"comments":     comments,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func addCommentHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
		return
	}

	recipeID := r.URL.Query().Get("recipeId")
	if recipeID == "" {
		http.Error(w, "Missing recipe ID", http.StatusBadRequest)
		return
	}

	var input struct {
		Comment string `json:"comment"`
	}
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil || input.Comment == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", recipeID, input.Comment)
	if err != nil {
		http.Error(w, "Failed to add comment", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func addRatingHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
		return
	}

	recipeID := r.URL.Query().Get("recipeId")
	if recipeID == "" {
		http.Error(w, "Missing recipe ID", http.StatusBadRequest)
		return
	}

	var input struct {
		Rating int `json:"rating"`
	}
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil || input.Rating < 1 || input.Rating > 5 {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", recipeID, input.Rating)
	if err != nil {
		http.Error(w, "Failed to add rating", http.StatusInternalServerError)
		return
	}

	// Update average rating
	_, err = db.Exec(`
		UPDATE recipes
		SET avg_rating = (
			SELECT AVG(rating) FROM ratings WHERE recipe_id = ?
		)
		WHERE id = ?`, recipeID, recipeID)
	if err != nil {
		http.Error(w, "Failed to update average rating", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func main() {
	initDatabase()
	defer db.Close()

	http.HandleFunc("/recipes", getRecipesHandler)
	http.HandleFunc("/recipes/upload", uploadRecipeHandler)
	http.HandleFunc("/recipes/", getRecipeHandler)
	http.HandleFunc("/recipes/comments", addCommentHandler)
	http.HandleFunc("/recipes/ratings", addRatingHandler)

	fmt.Println("Server running on http://0.0.0.0:5000")
	log.Fatal(http.ListenAndServe(":5000", nil))
}