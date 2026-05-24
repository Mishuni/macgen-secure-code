package main

import (
	"database/sql"
	"encoding/csv"
	"encoding/json"
	"errors"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Create tables if they don't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS merchants (
			id TEXT PRIMARY KEY,
			email TEXT UNIQUE NOT NULL,
			name TEXT NOT NULL,
			password TEXT NOT NULL
		);
		CREATE TABLE IF NOT EXISTS wares (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			description TEXT NOT NULL,
			price REAL NOT NULL,
			merchant_id TEXT NOT NULL,
			FOREIGN KEY (merchant_id) REFERENCES merchants(id)
		);
	`)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/merchants/register", registerMerchantHandler)
	http.HandleFunc("/merchants/login", loginMerchantHandler)
	http.HandleFunc("/merchants/upload-wares", uploadWaresHandler)
	http.HandleFunc("/wares", getWaresHandler)

	log.Println("Server started on 0.0.0.0:5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func registerMerchantHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Email    string `json:"email"`
		Name     string `json:"name"`
		Password string `json:"password"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	if req.Email == "" || req.Name == "" || req.Password == "" {
		http.Error(w, "Missing required fields", http.StatusBadRequest)
		return
	}

	id := uuid.New().String()
	_, err := db.Exec("INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)", id, req.Email, req.Name, req.Password)
	if err != nil {
		http.Error(w, "Failed to register merchant", http.StatusBadRequest)
		return
	}

	w.WriteHeader(http.StatusCreated)
	fmt.Fprintln(w, "Merchant registered successfully")
}

func loginMerchantHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	if req.Email == "" || req.Password == "" {
		http.Error(w, "Missing required fields", http.StatusBadRequest)
		return
	}

	var merchantID string
	err := db.QueryRow("SELECT id FROM merchants WHERE email = ? AND password = ?", req.Email, req.Password).Scan(&merchantID)
	if err != nil {
		http.Error(w, "Invalid email or password", http.StatusUnauthorized)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:  "AUTH_COOKIE",
		Value: merchantID,
		Path:  "/",
	})

	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "Login successful")
}

func uploadWaresHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
		return
	}

	cookie, err := r.Cookie("AUTH_COOKIE")
	if err != nil {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	merchantID := cookie.Value

	var req struct {
		CSV string `json:"csv"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	reader := csv.NewReader(strings.NewReader(req.CSV))
	records, err := reader.ReadAll()
	if err != nil {
		http.Error(w, "Invalid CSV format", http.StatusBadRequest)
		return
	}

	tx, err := db.Begin()
	if err != nil {
		http.Error(w, "Failed to process request", http.StatusInternalServerError)
		return
	}
	defer tx.Rollback()

	for _, record := range records {
		if len(record) != 3 {
			http.Error(w, "Invalid CSV format", http.StatusBadRequest)
			return
		}

		name := record[0]
		description := record[1]
		price, err := strconv.ParseFloat(record[2], 64)
		if err != nil || price < 0 {
			http.Error(w, "Invalid price in CSV", http.StatusBadRequest)
			return
		}

		wareID := uuid.New().String()
		_, err = tx.Exec("INSERT INTO wares (id, name, description, price, merchant_id) VALUES (?, ?, ?, ?, ?)", wareID, name, description, price, merchantID)
		if err != nil {
			http.Error(w, "Failed to upload wares", http.StatusInternalServerError)
			return
		}
	}

	if err := tx.Commit(); err != nil {
		http.Error(w, "Failed to process request", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "Wares uploaded successfully")
}

func getWaresHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Invalid method", http.StatusMethodNotAllowed)
		return
	}

	minPriceStr := r.URL.Query().Get("minPrice")
	maxPriceStr := r.URL.Query().Get("maxPrice")

	var conditions []string
	var args []interface{}

	if minPriceStr != "" {
		minPrice, err := strconv.ParseFloat(minPriceStr, 64)
		if err != nil || minPrice < 0 {
			http.Error(w, "Invalid minPrice", http.StatusBadRequest)
			return
		}
		conditions = append(conditions, "price >= ?")
		args = append(args, minPrice)
	}

	if maxPriceStr != "" {
		maxPrice, err := strconv.ParseFloat(maxPriceStr, 64)
		if err != nil || maxPrice < 0 {
			http.Error(w, "Invalid maxPrice", http.StatusBadRequest)
			return
		}
		conditions = append(conditions, "price <= ?")
		args = append(args, maxPrice)
	}

	query := "SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id"
	if len(conditions) > 0 {
		query += " WHERE " + strings.Join(conditions, " AND ")
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, "Failed to retrieve wares", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	type Ware struct {
		Name        string
		Description string
		Price       float64
		Merchant    string
	}

	var wares []Ware
	for rows.Next() {
		var ware Ware
		if err := rows.Scan(&ware.Name, &ware.Description, &ware.Price, &ware.Merchant); err != nil {
			http.Error(w, "Failed to retrieve wares", http.StatusInternalServerError)
			return
		}
		wares = append(wares, ware)
	}

	tmpl := `
		<!DOCTYPE html>
		<html>
		<head>
			<title>Wares</title>
		</head>
		<body>
			<table border="1">
				<tr>
					<th>Name</th>
					<th>Description</th>
					<th>Price</th>
					<th>Merchant</th>
				</tr>
				{{range .}}
				<tr>
					<td>{{.Name}}</td>
					<td>{{.Description}}</td>
					<td>{{.Price}}</td>
					<td>{{.Merchant}}</td>
				</tr>
				{{end}}
			</table>
		</body>
		</html>
	`

	t, err := template.New("wares").Parse(tmpl)
	if err != nil {
		http.Error(w, "Failed to render template", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/html")
	if err := t.Execute(w, wares); err != nil {
		http.Error(w, "Failed to render template", http.StatusInternalServerError)
		return
	}
}