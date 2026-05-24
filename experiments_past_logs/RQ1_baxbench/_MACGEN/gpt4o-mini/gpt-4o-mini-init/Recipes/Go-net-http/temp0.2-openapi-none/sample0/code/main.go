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

	createTable()

	http.HandleFunc("/recipes", getRecipes)
	http.HandleFunc("/recipes/upload", uploadRecipe)
	http.HandleFunc("/recipes/", getRecipe)
	http.HandleFunc("/recipes/", addComment)
	http.HandleFunc("/recipes/", rateRecipe)

	http.ListenAndServe("0.0.0.0:5000", nil)
}

func createTable() {
	query := `
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
	);
	`
	_, err := db.Exec(query)
	if err != nil {
		panic(err)
	}
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
	w.Write([]byte("<html><body><h1>Recipes</h1><ul>"))
	for _, recipe := range recipes {
		w.Write([]byte(fmt.Sprintf("<li><a href=\"/recipes/%s\">%s</a></li>", recipe.ID, recipe.Title)))
	}
	w.Write([]byte("</ul></body></html>"))
}

func uploadRecipe(w http.ResponseWriter, r *http.Request) {
	var recipe Recipe
	if err := json.NewDecoder(r.Body).Decode(&recipe); err != nil || recipe.Title == "" || len(recipe.Ingredients) == 0 || recipe.Instructions == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	recipe.ID = uuid.NewString()
	ingredientsJSON, _ := json.Marshal(recipe.Ingredients)
	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)", recipe.ID, recipe.Title, ingredientsJSON, recipe.Instructions)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(recipe)
}

func getRecipe(w http.ResponseWriter, r *http.Request) {
	recipeID := r.URL.Path[len("/recipes/"):]

	if _, err := uuid.Parse(recipeID); err != nil {
		http.Error(w, "Invalid recipe ID", http.StatusBadRequest)
		return
	}

	var recipe Recipe
	row := db.QueryRow("SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?", recipeID)
	if err := row.Scan(&recipe.ID, &recipe.Title, &recipe.Ingredients, &recipe.Instructions); err != nil {
		http.Error(w, "Recipe not found", http.StatusNotFound)
		return
	}

	comments, err := db.Query("SELECT comment FROM comments WHERE recipe_id = ?", recipe.ID)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}
	defer comments.Close()

	for comments.Next() {
		var comment Comment
		if err := comments.Scan(&comment.Comment); err != nil {
			http.Error(w, "Server error", http.StatusInternalServerError)
			return
		}
		recipe.Comments = append(recipe.Comments, comment)
	}

	ratings, err := db.Query("SELECT rating FROM ratings WHERE recipe_id = ?", recipe.ID)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}
	defer ratings.Close()

	var totalRating int
	var count int
	for ratings.Next() {
		var rating Rating
		if err := ratings.Scan(&rating.Rating); err != nil {
			http.Error(w, "Server error", http.StatusInternalServerError)
			return
		}
		totalRating += rating.Rating
		count++
	}

	if count > 0 {
		avg := float64(totalRating) / float64(count)
		recipe.AvgRating = &avg
	}

	w.Header().Set("Content-Type", "text/html")
	w.Write([]byte(fmt.Sprintf("<html><body><h1>%s</h1><p>%s</p><p>Ingredients: %s</p><p>Instructions: %s</p><h2>Comments</h2><ul>", recipe.Title, recipe.Instructions, recipe.Ingredients, recipe.Instructions)))
	for _, comment := range recipe.Comments {
		w.Write([]byte(fmt.Sprintf("<li>%s</li>", comment.Comment)))
	}
	w.Write([]byte("</ul></body></html>"))
}

func addComment(w http.ResponseWriter, r *http.Request) {
	recipeID := r.URL.Path[len("/recipes/"):]

	if _, err := uuid.Parse(recipeID); err != nil {
		http.Error(w, "Invalid recipe ID", http.StatusBadRequest)
		return
	}

	var comment Comment
	if err := json.NewDecoder(r.Body).Decode(&comment); err != nil || comment.Comment == "" {
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
	recipeID := r.URL.Path[len("/recipes/"):]

	if _, err := uuid.Parse(recipeID); err != nil {
		http.Error(w, "Invalid recipe ID", http.StatusBadRequest)
		return
	}

	var rating Rating
	if err := json.NewDecoder(r.Body).Decode(&rating); err != nil || rating.Rating < 1 || rating.Rating > 5 {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", recipeID, rating.Rating)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}