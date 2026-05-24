package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

type Product struct {
	ProductName string   `json:"product_name"`
	Tags        []string `json:"tags"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		logErrorAndRespond(err, "Database connection error", http.StatusInternalServerError)
		return
	}
	defer db.Close()

	// Create the products table if it doesn't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS products (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		tags TEXT NOT NULL
	)`)
	if err != nil {
		logErrorAndRespond(err, "Database setup error", http.StatusInternalServerError)
		return
	}

	http.HandleFunc("/recommender", recommenderHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func recommenderHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		handleGet(w, r)
	case http.MethodPost:
		handlePost(w, r)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func handleGet(w http.ResponseWriter, r *http.Request) {
	tagsParam := r.URL.Query().Get("tags")
	if tagsParam == "" {
		http.Error(w, "Tags are required", http.StatusBadRequest)
		return
	}

	tags := strings.Split(tagsParam, ",")
	if len(tags) > 10 { // Limit the number of tags to prevent DoS
		http.Error(w, "Too many tags", http.StatusBadRequest)
		return
	}

	query := "SELECT product_name, tags FROM products WHERE "
	for i, tag := range tags {
		if i > 0 {
			query += " OR "
		}
		query += "tags LIKE ?"
	}

	rows, err := db.Query(query, prepareTagsForQuery(tags)...)
	if err != nil {
		logErrorAndRespond(err, "Database query error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var products []string
	for rows.Next() {
		var productName, tags string
		if err := rows.Scan(&productName, &tags); err != nil {
			logErrorAndRespond(err, "Database scan error", http.StatusInternalServerError)
			return
		}
		products = append(products, fmt.Sprintf("<div><strong>%s</strong> - Tags: %s</div>", escapeHTML(productName), escapeHTML(tags)))
	}

	w.Header().Set("Content-Type", "text/html")
	if len(products) == 0 {
		fmt.Fprintln(w, "<div>No products found</div>")
	} else {
		fmt.Fprintln(w, strings.Join(products, ""))
	}
}

func handlePost(w http.ResponseWriter, r *http.Request) {
	var product Product
	if err := json.NewDecoder(r.Body).Decode(&product); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if product.ProductName == "" || len(product.Tags) == 0 {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	if !isValidInput(product.ProductName) || !areValidTags(product.Tags) {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	tags := strings.Join(product.Tags, ",")
	_, err := db.Exec("INSERT INTO products (product_name, tags) VALUES (?, ?)", product.ProductName, tags)
	if err != nil {
		logErrorAndRespond(err, "Database insert error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func prepareTagsForQuery(tags []string) []interface{} {
	var args []interface{}
	for _, tag := range tags {
		args = append(args, "%"+tag+"%")
	}
	return args
}

func escapeHTML(s string) string {
	return strings.ReplaceAll(strings.ReplaceAll(strings.ReplaceAll(strings.ReplaceAll(s, "&", "&amp;"), "<", "&lt;"), ">", "&gt;"), `"`, "&quot;"), `'`, "&#39;")
}

func isValidInput(input string) bool {
	// Basic validation for product name
	return regexp.MustCompile(`^[a-zA-Z0-9\s]+$`).MatchString(input)
}

func areValidTags(tags []string) bool {
	for _, tag := range tags {
		if !isValidInput(tag) {
			return false
		}
	}
	return true
}

func logErrorAndRespond(err error, message string, status int) {
	// Log the error internally (could be to a file or monitoring system)
	fmt.Println(err) // Replace with proper logging in production
	http.Error(w, message, status) // Correctly reference the response writer
}