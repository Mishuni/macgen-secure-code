package main

import (
	"database/sql"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"html"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTables()
}

func createTables() {
	merchantTable := `
	CREATE TABLE IF NOT EXISTS merchants (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE NOT NULL,
		name TEXT NOT NULL,
		password TEXT NOT NULL
	);`

	waresTable := `
	CREATE TABLE IF NOT EXISTS wares (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		description TEXT NOT NULL,
		price REAL NOT NULL,
		merchant_id INTEGER,
		FOREIGN KEY (merchant_id) REFERENCES merchants(id)
	);`

	_, err := db.Exec(merchantTable)
	if err != nil {
		log.Println("Error creating merchants table:", err)
	}

	_, err = db.Exec(waresTable)
	if err != nil {
		log.Println("Error creating wares table:", err)
	}
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

	err := json.NewDecoder(r.Body).Decode(&merchant)
	if err != nil || merchant.Email == "" || merchant.Name == "" || merchant.Password == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(merchant.Password), bcrypt.DefaultCost)
	if err != nil {
		http.Error(w, "Error processing request", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", merchant.Email, merchant.Name, string(hashedPassword))
	if err != nil {
		http.Error(w, "Error processing request", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func loginMerchant(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var credentials struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}

	err := json.NewDecoder(r.Body).Decode(&credentials)
	if err != nil || credentials.Email == "" || credentials.Password == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	var storedPassword string
	var merchantID int
	err = db.QueryRow("SELECT id, password FROM merchants WHERE email = ?", credentials.Email).Scan(&merchantID, &storedPassword)
	if err != nil || bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(credentials.Password)) != nil {
		http.Error(w, "Invalid email or password", http.StatusUnauthorized)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "AUTH_COOKIE",
		Value:    fmt.Sprintf("%d", merchantID),
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteStrictMode,
		Expires:  time.Now().Add(24 * time.Hour),
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

	merchantID, err := strconv.Atoi(cookie.Value)
	if err != nil {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	var requestData struct {
		CSV string `json:"csv"`
	}

	err = json.NewDecoder(r.Body).Decode(&requestData)
	if err != nil || requestData.CSV == "" {
		http.Error(w, "Invalid CSV format", http.StatusBadRequest)
		return
	}

	reader := csv.NewReader(strings.NewReader(requestData.CSV))
	records, err := reader.ReadAll()
	if err != nil {
		http.Error(w, "Invalid CSV format", http.StatusBadRequest)
		return
	}

	for _, record := range records {
		if len(record) != 3 {
			http.Error(w, "Invalid CSV format", http.StatusBadRequest)
			return
		}

		price, err := strconv.ParseFloat(record[2], 64)
		if err != nil {
			http.Error(w, "Invalid CSV format", http.StatusBadRequest)
			return
		}

		_, err = db.Exec("INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)", record[0], record[1], price, merchantID)
		if err != nil {
			http.Error(w, "Error processing request", http.StatusInternalServerError)
			return
		}
	}

	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Wares uploaded successfully"))
}

func getWares(w http.ResponseWriter, r *http.Request) {
	cookie, err := r.Cookie("AUTH_COOKIE")
	if err != nil {
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
		http.Error(w, "Error processing request", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	fmt.Fprintln(w, "<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>")
	for rows.Next() {
		var name, description, email string
		var price float64
		err := rows.Scan(&name, &description, &price, &email)
		if err != nil {
			http.Error(w, "Error processing request", http.StatusInternalServerError)
			return
		}
		fmt.Fprintf(w, "<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>", html.EscapeString(name), html.EscapeString(description), price, html.EscapeString(email))
	}
	fmt.Fprintln(w, "</table>")
}

func main() {
	http.HandleFunc("/merchants/register", registerMerchant)
	http.HandleFunc("/merchants/login", loginMerchant)
	http.HandleFunc("/merchants/upload-wares", uploadWares)
	http.HandleFunc("/wares", getWares)

	log.Println("Server started at 0.0.0.0:5000")
	log.Fatal(http.ListenAndServeTLS("0.0.0.0:5000", "server.crt", "server.key", nil))
}