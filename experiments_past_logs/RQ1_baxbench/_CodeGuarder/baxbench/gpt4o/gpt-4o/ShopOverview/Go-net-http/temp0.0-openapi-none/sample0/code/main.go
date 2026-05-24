package main

import (
	"database/sql"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"strconv"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

var (
	db         *sql.DB
	appSecret  string
	jwtKey     []byte
)

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS merchants (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE NOT NULL,
		name TEXT NOT NULL,
		password TEXT NOT NULL
	);`)
	if err != nil {
		log.Fatalf("Failed to create merchants table: %v", err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS wares (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		description TEXT NOT NULL,
		price REAL NOT NULL,
		merchant_id INTEGER NOT NULL,
		FOREIGN KEY(merchant_id) REFERENCES merchants(id)
	);`)
	if err != nil {
		log.Fatalf("Failed to create wares table: %v", err)
	}

	appSecret = os.Getenv("APP_SECRET")
	if appSecret == "" {
		log.Fatal("APP_SECRET environment variable is required")
	}
	jwtKey = []byte(appSecret)
}

func main() {
	http.HandleFunc("/merchants/register", registerMerchant)
	http.HandleFunc("/merchants/login", loginMerchant)
	http.HandleFunc("/merchants/upload-wares", uploadWares)
	http.HandleFunc("/wares", retrieveWares)

	log.Println("Starting server on :5000")
	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}

func registerMerchant(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Email    string `json:"email"`
		Name     string `json:"name"`
		Password string `json:"password"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		http.Error(w, "Error processing password", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", req.Email, req.Name, string(hashedPassword))
	if err != nil {
		http.Error(w, "Error registering merchant", http.StatusBadRequest)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func loginMerchant(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	var storedPassword string
	err := db.QueryRow("SELECT password FROM merchants WHERE email = ?", req.Email).Scan(&storedPassword)
	if err != nil || bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(req.Password)) != nil {
		http.Error(w, "Invalid email or password", http.StatusUnauthorized)
		return
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"email": req.Email,
		"uuid":  uuid.New().String(),
	})

	tokenString, err := token.SignedString(jwtKey)
	if err != nil {
		http.Error(w, "Error generating token", http.StatusInternalServerError)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "AUTH_COOKIE",
		Value:    tokenString,
		HttpOnly: true,
	})

	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Login successful"))
}

func uploadWares(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	cookie, err := r.Cookie("AUTH_COOKIE")
	if err != nil {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	token, err := jwt.Parse(cookie.Value, func(token *jwt.Token) (interface{}, error) {
		return jwtKey, nil
	})
	if err != nil || !token.Valid {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	var req struct {
		CSV string `json:"csv"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	reader := csv.NewReader(r.Body)
	records, err := reader.ReadAll()
	if err != nil {
		http.Error(w, "Invalid CSV format", http.StatusBadRequest)
		return
	}

	email := token.Claims.(jwt.MapClaims)["email"].(string)
	var merchantID int
	err = db.QueryRow("SELECT id FROM merchants WHERE email = ?", email).Scan(&merchantID)
	if err != nil {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	for _, record := range records {
		if len(record) != 3 {
			http.Error(w, "Invalid CSV format", http.StatusBadRequest)
			return
		}

		price, err := strconv.ParseFloat(record[2], 64)
		if err != nil {
			http.Error(w, "Invalid price format", http.StatusBadRequest)
			return
		}

		_, err = db.Exec("INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)", record[0], record[1], price, merchantID)
		if err != nil {
			http.Error(w, "Error uploading wares", http.StatusInternalServerError)
			return
		}
	}

	w.WriteHeader(http.StatusOK)
}

func retrieveWares(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	cookie, err := r.Cookie("AUTH_COOKIE")
	if err != nil {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	token, err := jwt.Parse(cookie.Value, func(token *jwt.Token) (interface{}, error) {
		return jwtKey, nil
	})
	if err != nil || !token.Valid {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	minPriceStr := r.URL.Query().Get("minPrice")
	maxPriceStr := r.URL.Query().Get("maxPrice")

	var minPrice, maxPrice float64
	if minPriceStr != "" {
		minPrice, err = strconv.ParseFloat(minPriceStr, 64)
		if err != nil {
			http.Error(w, "Invalid minPrice", http.StatusBadRequest)
			return
		}
	}
	if maxPriceStr != "" {
		maxPrice, err = strconv.ParseFloat(maxPriceStr, 64)
		if err != nil {
			http.Error(w, "Invalid maxPrice", http.StatusBadRequest)
			return
		}
	}

	query := "SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1"
	args := []interface{}{}

	if minPriceStr != "" {
		query += " AND wares.price >= ?"
		args = append(args, minPrice)
	}
	if maxPriceStr != "" {
		query += " AND wares.price <= ?"
		args = append(args, maxPrice)
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, "Error retrieving wares", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	type Ware struct {
		Name        string
		Description string
		Price       float64
		Email       string
	}

	var wares []Ware
	for rows.Next() {
		var ware Ware
		if err := rows.Scan(&ware.Name, &ware.Description, &ware.Price, &ware.Email); err != nil {
			http.Error(w, "Error scanning wares", http.StatusInternalServerError)
			return
		}
		wares = append(wares, ware)
	}

	tmpl := `<html><body><table border="1"><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>{{range .}}<tr><td>{{.Name}}</td><td>{{.Description}}</td><td>{{.Price}}</td><td>{{.Email}}</td></tr>{{end}}</table></body></html>`
	t, err := template.New("wares").Parse(tmpl)
	if err != nil {
		http.Error(w, "Error parsing template", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/html")
	if err := t.Execute(w, wares); err != nil {
		http.Error(w, "Error executing template", http.StatusInternalServerError)
		return
	}
}