package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"strconv"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Recipe struct {
	ID           string   `json:"id"`
	Title        string   `json:"title"`
	Ingredients  []string `json:"ingredients"`
	Instructions string   `json:"instructions"`
	Comments     []string `json:"comments"`
	AvgRating    float64  `json:"avgRating"`
}

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS recipes (
		id TEXT PRIMARY KEY,
		title TEXT,
		ingredients TEXT,
		instructions TEXT,
		comments TEXT,
		avgRating REAL
	);
	`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		log.Fatal(err)
	}
}

func getRecipesHandler(w http.ResponseWriter, r *http.Request) {
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

	tmpl := `<html><body><h1>Recipes</h1><ul>{{range .}}<li><a href="/recipes/{{.ID}}">{{.Title}}</a></li>{{end}}</ul></body></html>`
	t, err := template.New("recipes").Parse(tmpl)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}
	t.Execute(w, recipes)
}

func uploadRecipeHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var recipe Recipe
	if err := json.NewDecoder(r.Body).Decode(&recipe); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	recipe.ID = uuid.New().String()
	recipe.Comments = []string{}
	recipe.AvgRating = 0.0

	ingredients, err := json.Marshal(recipe.Ingredients)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("INSERT INTO recipes (id, title, ingredients, instructions, comments, avgRating) VALUES (?, ?, ?, ?, ?, ?)",
		recipe.ID, recipe.Title, string(ingredients), recipe.Instructions, "[]", recipe.AvgRating)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(recipe)
}

func getRecipeHandler(w http.ResponseWriter, r *http.Request) {
	recipeID := r.URL.Path[len("/recipes/"):]

	row := db.QueryRow("SELECT id, title, ingredients, instructions, comments, avgRating FROM recipes WHERE id = ?", recipeID)

	var recipe Recipe
	var ingredients, comments string
	if err := row.Scan(&recipe.ID, &recipe.Title, &ingredients, &recipe.Instructions, &comments, &recipe.AvgRating); err != nil {
		http.Error(w, "Recipe not found", http.StatusNotFound)
		return
	}

	if err := json.Unmarshal([]byte(ingredients), &recipe.Ingredients); err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	if err := json.Unmarshal([]byte(comments), &recipe.Comments); err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	tmpl := `<html><body><h1>{{.Title}}</h1><p>{{.Instructions}}</p><h2>Ingredients</h2><ul>{{range .Ingredients}}<li>{{.}}</li>{{end}}</ul><h2>Comments</h2><ul>{{range .Comments}}<li>{{.}}</li>{{end}}</ul><h2>Average Rating: {{.AvgRating}}</h2></body></html>`
	t, err := template.New("recipe").Parse(tmpl)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}
	t.Execute(w, recipe)
}

func addCommentHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	recipeID := r.URL.Path[len("/recipes/"):len("/recipes/")+36]
	var input struct {
		Comment string `json:"comment"`
	}
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	row := db.QueryRow("SELECT comments FROM recipes WHERE id = ?", recipeID)
	var comments string
	if err := row.Scan(&comments); err != nil {
		http.Error(w, "Recipe not found", http.StatusNotFound)
		return
	}

	var commentList []string
	if err := json.Unmarshal([]byte(comments), &commentList); err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	commentList = append(commentList, input.Comment)
	updatedComments, err := json.Marshal(commentList)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("UPDATE recipes SET comments = ? WHERE id = ?", string(updatedComments), recipeID)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func rateRecipeHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	recipeID := r.URL.Path[len("/recipes/"):len("/recipes/")+36]
	var input struct {
		Rating int `json:"rating"`
	}
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if input.Rating < 1 || input.Rating > 5 {
		http.Error(w, "Invalid rating", http.StatusBadRequest)
		return
	}

	row := db.QueryRow("SELECT avgRating FROM recipes WHERE id = ?", recipeID)
	var avgRating float64
	if err := row.Scan(&avgRating); err != nil {
		http.Error(w, "Recipe not found", http.StatusNotFound)
		return
	}

	newAvgRating := (avgRating + float64(input.Rating)) / 2
	_, err := db.Exec("UPDATE recipes SET avgRating = ? WHERE id = ?", newAvgRating, recipeID)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/recipes", getRecipesHandler)
	http.HandleFunc("/recipes/upload", uploadRecipeHandler)
	http.HandleFunc("/recipes/", getRecipeHandler)
	http.HandleFunc("/recipes/", addCommentHandler)
	http.HandleFunc("/recipes/", rateRecipeHandler)

	fmt.Println("Server started at http://0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}