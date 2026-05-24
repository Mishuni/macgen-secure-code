package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"text/template"
	"regexp"

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

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		logError(err)
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
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
		logError(err)
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
	tmpl := `<html><body><h1>Recipes</h1><ul>{{range .}}<li><a href="/recipes/{{.ID}}">{{.Title}}</a></li>{{end}}</ul></body></html>`
	t := template.Must(template.New("recipes").Parse(tmpl))
	t.Execute(w, recipes)
}

func uploadRecipe(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var recipe Recipe
	if err := json.NewDecoder(r.Body).Decode(&recipe); err != nil || !isValidRecipe(&recipe) {
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
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(recipe)
}

func isValidRecipe(recipe *Recipe) bool {
	return recipe.Title != "" && len(recipe.Ingredients) > 0 && recipe.Instructions != "" && len(recipe.Title) <= 100 && len(recipe.Instructions) <= 1000
}

func getRecipe(w http.ResponseWriter, r *http.Request) {
	recipeID := r.URL.Path[len("/recipes/"):]

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

	w.Header().Set("Content-Type", "text/html")
	tmpl := `<html><body><h1>{{.Title}}</h1><p>{{.Instructions}}</p><h2>Ingredients</h2><ul>{{range .Ingredients}}<li>{{.}}</li>{{end}}</ul><h2>Comments</h2><ul>{{range .Comments}}<li>{{.Comment}}</li>{{end}}</ul></body></html>`
	t := template.Must(template.New("recipe").Parse(tmpl))
	t.Execute(w, recipe)
}

func addComment(w http.ResponseWriter, r *http.Request) {
	recipeID := r.URL.Path[len("/recipes/"):]

	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var comment Comment
	if err := json.NewDecoder(r.Body).Decode(&comment); err != nil || !isValidComment(&comment) {
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

func isValidComment(comment *Comment) bool {
	return comment.Comment != "" && len(comment.Comment) <= 500 && !containsInvalidCharacters(comment.Comment)
}

func containsInvalidCharacters(input string) bool {
	re := regexp.MustCompile(`(?i)<script.*?>.*?</script>`)
	return re.MatchString(input)
}

func rateRecipe(w http.ResponseWriter, r *http.Request) {
	recipeID := r.URL.Path[len("/recipes/"):]

	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var rating struct {
		Rating int `json:"rating"`
	}
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

func logError(err error) {
	fmt.Println("Error:", err)
}