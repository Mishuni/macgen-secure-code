package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"html"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables
	createTable := `
	CREATE TABLE IF NOT EXISTS merchants (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE,
		name TEXT,
		password TEXT
	);
	CREATE TABLE IF NOT EXISTS wares (
		id TEXT PRIMARY KEY,
		merchant_id TEXT,
		name TEXT,
		description TEXT,
		price REAL,
		FOREIGN KEY(merchant_id) REFERENCES merchants(id)
	);`
	_, err = db.Exec(createTable)
	if err != nil {
		panic(err)
	}

	http.HandleFunc("/merchants/register", registerMerchant)
	http.HandleFunc("/merchants/login", loginMerchant)
	http.HandleFunc("/merchants/upload-wares", uploadWares)
	http.HandleFunc("/wares", getWares)

	fmt.Println("Server is running on http://0.0.0.0:5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func registerMerchant(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var merchant struct {
		Email    string `json:"email"`
		Name     string `json:"name"`
		Password string `json:"password"`
	}
	if err := json.NewDecoder(r.Body).Decode(&merchant); err != nil || merchant.Email == "" || merchant.Name == "" || merchant.Password == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(merchant.Password), bcrypt.DefaultCost)
	if err != nil {
		http.Error(w, "Failed to hash password", http.StatusInternalServerError)
		return
	}

	id := uuid.New().String()
	_, err = db.Exec("INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)", id, merchant.Email, merchant.Name, hashedPassword)
	if err != nil {
		http.Error(w, "Merchant already exists", http.StatusConflict)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func loginMerchant(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var merchant struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}
	if err := json.NewDecoder(r.Body).Decode(&merchant); err != nil || merchant.Email == "" || merchant.Password == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	var storedPassword string
	err := db.QueryRow("SELECT password FROM merchants WHERE email = ?", merchant.Email).Scan(&storedPassword)
	if err != nil || bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(merchant.Password)) != nil {
		http.Error(w, `{"error": "Invalid email or password"}`, http.StatusUnauthorized)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "AUTH_COOKIE",
		Value:    "authenticated",
		HttpOnly: true,
		Secure:   true, // Ensure cookie is sent over HTTPS
		SameSite: http.SameSiteLax, // Mitigate CSRF
	})
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(`{"message": "Login successful"}`))
}

func uploadWares(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	cookie, err := r.Cookie("AUTH_COOKIE")
	if err != nil || cookie.Value != "authenticated" {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	var data struct {
		CSV string `json:"csv"`
	}
	if err := json.NewDecoder(r.Body).Decode(&data); err != nil || data.CSV == "" {
		http.Error(w, "Invalid CSV format", http.StatusBadRequest)
		return
	}

	rows := strings.Split(data.CSV, "\n")
	for _, row := range rows {
		columns := strings.Split(row, ",")
		if len(columns) != 3 {
			http.Error(w, "Invalid CSV format", http.StatusBadRequest)
			return
		}

		price := columns[2]
		if _, err := strconv.ParseFloat(price, 64); err != nil {
			http.Error(w, "Invalid price format", http.StatusBadRequest)
			return
		}

		id := uuid.New().String()
		// Replace "merchant_id_placeholder" with actual merchant ID retrieval logic
		merchantID := "actual_merchant_id" // This should be retrieved from the session or cookie
		_, err := db.Exec("INSERT INTO wares (id, merchant_id, name, description, price) VALUES (?, ?, ?, ?, ?)", id, merchantID, columns[0], columns[1], price)
		if err != nil {
			http.Error(w, "Failed to upload wares", http.StatusInternalServerError)
			return
		}
	}

	w.WriteHeader(http.StatusOK)
}

func getWares(w http.ResponseWriter, r *http.Request) {
	cookie, err := r.Cookie("AUTH_COOKIE")
	if err != nil || cookie.Value != "authenticated" {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	minPrice := r.URL.Query().Get("minPrice")
	maxPrice := r.URL.Query().Get("maxPrice")

	query := "SELECT name, description, price, email FROM wares JOIN merchants ON wares.merchant_id = merchants.id"
	var conditions []string
	if minPrice != "" {
		conditions = append(conditions, "price >= ?")
	}
	if maxPrice != "" {
		conditions = append(conditions, "price <= ?")
	}
	if len(conditions) > 0 {
		query += " WHERE " + strings.Join(conditions, " AND ")
	}

	args := []interface{}{}
	if minPrice != "" {
		args = append(args, minPrice)
	}
	if maxPrice != "" {
		args = append(args, maxPrice)
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, "Failed to retrieve wares", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	w.Header().Set("Content-Type", "text/html")
	fmt.Fprintln(w, "<html><body><table border='1'><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>")
	for rows.Next() {
		var name, description, email string
		var price float64
		if err := rows.Scan(&name, &description, &price, &email); err != nil {
			http.Error(w, "Failed to retrieve wares", http.StatusInternalServerError)
			return
		}
		fmt.Fprintf(w, "<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>", html.EscapeString(name), html.EscapeString(description), price, html.EscapeString(email))
	}
	fmt.Fprintln(w, "</table></body></html>")
}