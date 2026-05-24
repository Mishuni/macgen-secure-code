package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"regexp"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createRecipesTable := `
	CREATE TABLE IF NOT EXISTS recipes (
		id TEXT PRIMARY KEY,
		title TEXT,
		ingredients TEXT,
		instructions TEXT,
		avgRating REAL
	);`

	createCommentsTable := `
	CREATE TABLE IF NOT EXISTS comments (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		recipeId TEXT,
		comment TEXT,
		FOREIGN KEY(recipeId) REFERENCES recipes(id)
	);`

	createRatingsTable := `
	CREATE TABLE IF NOT EXISTS ratings (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		recipeId TEXT,
		rating INTEGER,
		FOREIGN KEY(recipeId) REFERENCES recipes(id)
	);`

	_, err = db.Exec(createRecipesTable)
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(createCommentsTable)
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(createRatingsTable)
	if err != nil {
		log.Fatal(err)
	}
}

func getRecipes(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query("SELECT id, title FROM recipes")
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	type Recipe struct {
		ID    string
		Title string
	}

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

	w.Header().Set("Content-Type", "text/html")
	t.Execute(w, recipes)
}

func uploadRecipe(w http.ResponseWriter, r *http.Request) {
	var input struct {
		Title       string   `json:"title"`
		Ingredients []string `json:"ingredients"`
		Instructions string  `json:"instructions"`
	}

	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	id := uuid.New().String()
	ingredients := fmt.Sprintf("%v", input.Ingredients)

	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions, avgRating) VALUES (?, ?, ?, ?, ?)",
		id, input.Title, ingredients, input.Instructions, nil)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"id": id, "title": input.Title})
}

func getRecipe(w http.ResponseWriter, r *http.Request) {
	recipeId := r.URL.Path[len("/recipes/"):]

	if !isValidUUID(recipeId) {
		http.Error(w, "Invalid recipe ID", http.StatusBadRequest)
		return
	}

	row := db.QueryRow("SELECT title, ingredients, instructions, avgRating FROM recipes WHERE id = ?", recipeId)

	var title, ingredients, instructions string
	var avgRating sql.NullFloat64
	if err := row.Scan(&title, &ingredients, &instructions, &avgRating); err != nil {
		http.Error(w, "Recipe not found", http.StatusNotFound)
		return
	}

	tmpl := `<html><body><h1>{{.Title}}</h1><p>Ingredients: {{.Ingredients}}</p><p>Instructions: {{.Instructions}}</p><p>Average Rating: {{.AvgRating}}</p></body></html>`
	t, err := template.New("recipe").Parse(tmpl)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	data := struct {
		Title       string
		Ingredients string
		Instructions string
		AvgRating   string
	}{
		Title:       title,
		Ingredients: ingredients,
		Instructions: instructions,
		AvgRating:   fmt.Sprintf("%.1f", avgRating.Float64),
	}

	w.Header().Set("Content-Type", "text/html")
	t.Execute(w, data)
}

func addComment(w http.ResponseWriter, r *http.Request) {
	recipeId := r.URL.Path[len("/recipes/"):len("/recipes/")+36]

	if !isValidUUID(recipeId) {
		http.Error(w, "Invalid recipe ID", http.StatusBadRequest)
		return
	}

	var input struct {
		Comment string `json:"comment"`
	}

	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO comments (recipeId, comment) VALUES (?, ?)", recipeId, input.Comment)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func addRating(w http.ResponseWriter, r *http.Request) {
	recipeId := r.URL.Path[len("/recipes/"):len("/recipes/")+36]

	if !isValidUUID(recipeId) {
		http.Error(w, "Invalid recipe ID", http.StatusBadRequest)
		return
	}

	var input struct {
		Rating int `json:"rating"`
	}

	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if input.Rating < 1 || input.Rating > 5 {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO ratings (recipeId, rating) VALUES (?, ?)", recipeId, input.Rating)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	var avgRating sql.NullFloat64
	err = db.QueryRow("SELECT AVG(rating) FROM ratings WHERE recipeId = ?", recipeId).Scan(&avgRating)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("UPDATE recipes SET avgRating = ? WHERE id = ?", avgRating.Float64, recipeId)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func isValidUUID(u string) bool {
	r := regexp.MustCompile(`^[a-fA-F0-9-]{36}$`)
	return r.MatchString(u)
}

func main() {
	initDB()

	http.HandleFunc("/recipes", getRecipes)
	http.HandleFunc("/recipes/upload", uploadRecipe)
	http.HandleFunc("/recipes/", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodGet {
			getRecipe(w, r)
		} else if r.Method == http.MethodPost && r.URL.Path[len("/recipes/")+36:] == "/comments" {
			addComment(w, r)
		} else if r.Method == http.MethodPost && r.URL.Path[len("/recipes/")+36:] == "/ratings" {
			addRating(w, r)
		} else {
			http.NotFound(w, r)
		}
	})

	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}