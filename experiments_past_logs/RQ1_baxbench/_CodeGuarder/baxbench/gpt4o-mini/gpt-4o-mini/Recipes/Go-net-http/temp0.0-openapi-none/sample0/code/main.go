package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Recipe struct {
	ID          string   `json:"id"`
	Title       string   `json:"title"`
	Ingredients []string `json:"ingredients"`
	Instructions string   `json:"instructions"`
	Comments    []Comment `json:"comments"`
	AvgRating   *float64 `json:"avgRating,omitempty"`
}

type Comment struct {
	Comment string `json:"comment"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}

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
}

func main() {
	http.HandleFunc("/recipes", getRecipes)
	http.HandleFunc("/recipes/upload", uploadRecipe)
	http.HandleFunc("/recipes/", getRecipeByID)
	http.HandleFunc("/recipes/", addComment)
	http.HandleFunc("/recipes/", rateRecipe)

	http.ListenAndServe("0.0.0.0:5000", nil)
}

func getRecipes(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query("SELECT id, title FROM recipes")
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var recipes []Recipe
	for rows.Next() {
		var recipe Recipe
		if err := rows.Scan(&recipe.ID, &recipe.Title); err != nil {
			http.Error(w, "Server error", http.StatusInternalServerError)
			return
		}
		recipes = append(recipes, recipe)
	}

	w.Header().Set("Content-Type", "text/html")
	fmt.Fprintf(w, "<html><body><h1>Recipes</h1><ul>")
	for _, recipe := range recipes {
		fmt.Fprintf(w, "<li><a href=\"/recipes/%s\">%s</a></li>", recipe.ID, recipe.Title)
	}
	fmt.Fprintf(w, "</ul></body></html>")
}

func uploadRecipe(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var recipe Recipe
	if err := json.NewDecoder(r.Body).Decode(&recipe); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	recipe.ID = uuid.NewString()
	ingredientsJSON, _ := json.Marshal(recipe.Ingredients)

	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)",
		recipe.ID, recipe.Title, string(ingredientsJSON), recipe.Instructions)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(recipe)
}

func getRecipeByID(w http.ResponseWriter, r *http.Request) {
	recipeID := r.URL.Path[len("/recipes/"):]

	var recipe Recipe
	row := db.QueryRow("SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?", recipeID)
	var ingredientsJSON string
	if err := row.Scan(&recipe.ID, &recipe.Title, &ingredientsJSON, &recipe.Instructions); err != nil {
		http.Error(w, "Recipe not found", http.StatusNotFound)
		return
	}

	json.Unmarshal([]byte(ingredientsJSON), &recipe.Ingredients)
	w.Header().Set("Content-Type", "text/html")
	fmt.Fprintf(w, "<html><body><h1>%s</h1><p>%s</p><h2>Ingredients</h2><ul>", recipe.Title, recipe.Instructions)
	for _, ingredient := range recipe.Ingredients {
		fmt.Fprintf(w, "<li>%s</li>", ingredient)
	}
	fmt.Fprintf(w, "</ul></body></html>")
}

func addComment(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	recipeID := r.URL.Path[len("/recipes/"):]

	var comment Comment
	if err := json.NewDecoder(r.Body).Decode(&comment); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", recipeID, comment.Comment)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func rateRecipe(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	recipeID := r.URL.Path[len("/recipes/"):]

	var rating struct {
		Rating int `json:"rating"`
	}
	if err := json.NewDecoder(r.Body).Decode(&rating); err != nil || rating.Rating < 1 || rating.Rating > 5 {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	// Logic to update the average rating would go here

	w.WriteHeader(http.StatusCreated)
}