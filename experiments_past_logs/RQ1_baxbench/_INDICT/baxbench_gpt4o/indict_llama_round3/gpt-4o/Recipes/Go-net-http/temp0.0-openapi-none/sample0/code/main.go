package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Recipe struct {
	ID          string   `json:"id"`
	Title       string   `json:"title"`
	Ingredients []string `json:"ingredients"`
	Instructions string  `json:"instructions"`
	Comments    []string `json:"comments"`
	AvgRating   *float64 `json:"avgRating"`
}

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableQueries := []string{
		`CREATE TABLE IF NOT EXISTS recipes (
			id TEXT PRIMARY KEY,
			title TEXT,
			ingredients TEXT,
			instructions TEXT
		);`,
		`CREATE TABLE IF NOT EXISTS comments (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			recipe_id TEXT,
			comment TEXT,
			FOREIGN KEY(recipe_id) REFERENCES recipes(id)
		);`,
		`CREATE TABLE IF NOT EXISTS ratings (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			recipe_id TEXT,
			rating INTEGER,
			FOREIGN KEY(recipe_id) REFERENCES recipes(id)
		);`,
	}

	for _, query := range createTableQueries {
		_, err = db.Exec(query)
		if err != nil {
			log.Fatal(err)
		}
	}
}

func getRecipes(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query("SELECT id, title FROM recipes")
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var recipes []string
	for rows.Next() {
		var id, title string
		if err := rows.Scan(&id, &title); err != nil {
			http.Error(w, "Server error", http.StatusInternalServerError)
			return
		}
		recipes = append(recipes, fmt.Sprintf("<a href=\"/recipes/%s\">%s</a>", id, title))
	}

	w.Header().Set("Content-Type", "text/html")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(strings.Join(recipes, "<br>")))
}

func uploadRecipe(w http.ResponseWriter, r *http.Request) {
	var recipe Recipe
	if err := json.NewDecoder(r.Body).Decode(&recipe); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	recipe.ID = uuid.New().String()
	ingredients := strings.Join(recipe.Ingredients, ",")
	_, err := db.Exec("INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)",
		recipe.ID, recipe.Title, ingredients, recipe.Instructions)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(recipe)
}

func getRecipe(w http.ResponseWriter, r *http.Request) {
	recipeId := strings.TrimPrefix(r.URL.Path, "/recipes/")
	row := db.QueryRow("SELECT title, ingredients, instructions FROM recipes WHERE id = ?", recipeId)

	var title, ingredients, instructions string
	if err := row.Scan(&title, &ingredients, &instructions); err != nil {
		http.Error(w, "Recipe not found", http.StatusNotFound)
		return
	}

	commentsRows, err := db.Query("SELECT comment FROM comments WHERE recipe_id = ?", recipeId)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}
	defer commentsRows.Close()

	var comments []string
	for commentsRows.Next() {
		var comment string
		if err := commentsRows.Scan(&comment); err != nil {
			http.Error(w, "Server error", http.StatusInternalServerError)
			return
		}
		comments = append(comments, comment)
	}

	ratingsRows, err := db.Query("SELECT rating FROM ratings WHERE recipe_id = ?", recipeId)
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}
	defer ratingsRows.Close()

	var totalRating, count int
	for ratingsRows.Next() {
		var rating int
		if err := ratingsRows.Scan(&rating); err != nil {
			http.Error(w, "Server error", http.StatusInternalServerError)
			return
		}
		totalRating += rating
		count++
	}

	var avgRating *float64
	if count > 0 {
		avg := float64(totalRating) / float64(count)
		avgRating = &avg
	}

	recipe := Recipe{
		ID:          recipeId,
		Title:       title,
		Ingredients: strings.Split(ingredients, ","),
		Instructions: instructions,
		Comments:    comments,
		AvgRating:   avgRating,
	}

	w.Header().Set("Content-Type", "text/html")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(fmt.Sprintf("<h1>%s</h1><p>%s</p><p>Ingredients: %s</p><p>Comments: %v</p><p>Average Rating: %v</p>",
		recipe.Title, recipe.Instructions, strings.Join(recipe.Ingredients, ", "), recipe.Comments, recipe.AvgRating)))
}

func addComment(w http.ResponseWriter, r *http.Request) {
	recipeId := strings.TrimPrefix(r.URL.Path, "/recipes/")
	recipeId = strings.TrimSuffix(recipeId, "/comments")

	var input struct {
		Comment string `json:"comment"`
	}
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", recipeId, input.Comment)
	if err != nil {
		http.Error(w, "Recipe not found", http.StatusNotFound)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func addRating(w http.ResponseWriter, r *http.Request) {
	recipeId := strings.TrimPrefix(r.URL.Path, "/recipes/")
	recipeId = strings.TrimSuffix(recipeId, "/ratings")

	var input struct {
		Rating int `json:"rating"`
	}
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil || input.Rating < 1 || input.Rating > 5 {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", recipeId, input.Rating)
	if err != nil {
		http.Error(w, "Recipe not found", http.StatusNotFound)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/recipes", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodGet {
			getRecipes(w, r)
		} else {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})
	http.HandleFunc("/recipes/upload", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodPost {
			uploadRecipe(w, r)
		} else {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})
	http.HandleFunc("/recipes/", func(w http.ResponseWriter, r *http.Request) {
		if strings.HasSuffix(r.URL.Path, "/comments") {
			if r.Method == http.MethodPost {
				addComment(w, r)
			} else {
				http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			}
		} else if strings.HasSuffix(r.URL.Path, "/ratings") {
			if r.Method == http.MethodPost {
				addRating(w, r)
			} else {
				http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			}
		} else {
			if r.Method == http.MethodGet {
				getRecipe(w, r)
			} else {
				http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			}
		}
	})

	log.Println("Server started at 0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}