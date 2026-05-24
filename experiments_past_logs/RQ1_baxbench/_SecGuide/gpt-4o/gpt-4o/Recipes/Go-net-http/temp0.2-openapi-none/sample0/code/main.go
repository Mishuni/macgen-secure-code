package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"github.com/gorilla/mux"
)

type Recipe struct {
	ID          string   `json:"id"`
	Title       string   `json:"title"`
	Ingredients []string `json:"ingredients"`
	Instructions string  `json:"instructions"`
	Comments    []string `json:"comments"`
	AvgRating   float64  `json:"avgRating"`
}

var db *sql.DB

func initDB() {
	var err error
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "./db.sqlite3"
	}
	db, err = sql.Open("sqlite3", dbPath)
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

func main() {
	initDB()
	defer db.Close()

	r := mux.NewRouter()
	r.HandleFunc("/recipes", getRecipes).Methods(http.MethodGet)
	r.HandleFunc("/recipes/upload", uploadRecipe).Methods(http.MethodPost)
	r.HandleFunc("/recipes/{id}", getRecipe).Methods(http.MethodGet)
	r.HandleFunc("/recipes/{id}/comments", addComment).Methods(http.MethodPost)
	r.HandleFunc("/recipes/{id}/ratings", addRating).Methods(http.MethodPost)

	http.Handle("/", r)

	log.Println("Server started at http://0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
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

	tmpl := template.Must(template.New("recipes").Parse(`
		<html>
		<head><title>Recipes</title></head>
		<body>
		<h1>Recipes</h1>
		<ul>
		{{range .}}
			<li><a href="/recipes/{{.ID}}">{{.Title}}</a></li>
		{{end}}
		</ul>
		</body>
		</html>
	`))

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	tmpl.Execute(w, recipes)
}

func uploadRecipe(w http.ResponseWriter, r *http.Request) {
	var recipe Recipe
	if err := json.NewDecoder(r.Body).Decode(&recipe); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if recipe.Title == "" || len(recipe.Ingredients) == 0 || recipe.Instructions == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	recipe.ID = uuid.New().String()
	ingredients := strings.Join(recipe.Ingredients, ",")
	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions, comments, avgRating) VALUES (?, ?, ?, ?, ?, ?)",
		recipe.ID, recipe.Title, ingredients, recipe.Instructions, "", nil)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(recipe)
}

func getRecipe(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	recipeID := vars["id"]

	var recipe Recipe
	var ingredients, comments string
	err := db.QueryRow("SELECT id, title, ingredients, instructions, comments, avgRating FROM recipes WHERE id = ?", recipeID).
		Scan(&recipe.ID, &recipe.Title, &ingredients, &recipe.Instructions, &comments, &recipe.AvgRating)
	if err == sql.ErrNoRows {
		http.Error(w, "Recipe not found", http.StatusNotFound)
		return
	} else if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	recipe.Ingredients = strings.Split(ingredients, ",")
	recipe.Comments = strings.Split(comments, ",")

	tmpl := template.Must(template.New("recipe").Parse(`
		<html>
		<head><title>{{.Title}}</title></head>
		<body>
		<h1>{{.Title}}</h1>
		<h2>Ingredients</h2>
		<ul>
		{{range .Ingredients}}
			<li>{{.}}</li>
		{{end}}
		</ul>
		<h2>Instructions</h2>
		<p>{{.Instructions}}</p>
		<h2>Comments</h2>
		<ul>
		{{range .Comments}}
			<li>{{.}}</li>
		{{end}}
		</ul>
		<h2>Average Rating</h2>
		<p>{{.AvgRating}}</p>
		</body>
		</html>
	`))

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	tmpl.Execute(w, recipe)
}

func addComment(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	recipeID := vars["id"]

	var input struct {
		Comment string `json:"comment"`
	}
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if input.Comment == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	var comments string
	err := db.QueryRow("SELECT comments FROM recipes WHERE id = ?", recipeID).Scan(&comments)
	if err == sql.ErrNoRows {
		http.Error(w, "Recipe not found", http.StatusNotFound)
		return
	} else if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	comments = strings.TrimSpace(comments)
	if comments != "" {
		comments += ","
	}
	comments += input.Comment

	_, err = db.Exec("UPDATE recipes SET comments = ? WHERE id = ?", comments, recipeID)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func addRating(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	recipeID := vars["id"]

	var input struct {
		Rating int `json:"rating"`
	}
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil || input.Rating < 1 || input.Rating > 5 {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	var totalRatings int
	var sumRatings float64
	err := db.QueryRow("SELECT COUNT(*), SUM(avgRating) FROM recipes WHERE id = ?", recipeID).Scan(&totalRatings, &sumRatings)
	if err == sql.ErrNoRows {
		http.Error(w, "Recipe not found", http.StatusNotFound)
		return
	} else if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	totalRatings++
	sumRatings += float64(input.Rating)
	avgRating := sumRatings / float64(totalRatings)

	_, err = db.Exec("UPDATE recipes SET avgRating = ? WHERE id = ?", avgRating, recipeID)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}