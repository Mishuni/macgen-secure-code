package main

import (
	"database/sql"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

var db *sql.DB

type Merchant struct {
	ID       string
	Email    string
	Name     string
	Password string
}

type Ware struct {
	Name        string
	Description string
	Price       float64
	MerchantID  string
}

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createMerchantTable := `
	CREATE TABLE IF NOT EXISTS merchants (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE,
		name TEXT,
		password TEXT
	);`

	createWaresTable := `
	CREATE TABLE IF NOT EXISTS wares (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT,
		description TEXT,
		price REAL,
		merchant_id TEXT,
		FOREIGN KEY(merchant_id) REFERENCES merchants(id)
	);`

	_, err = db.Exec(createMerchantTable)
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(createWaresTable)
	if err != nil {
		log.Fatal(err)
	}
}

func registerMerchant(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var m Merchant
	err := json.NewDecoder(r.Body).Decode(&m)
	if err != nil || m.Email == "" || m.Name == "" || m.Password == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(m.Password), bcrypt.DefaultCost)
	if err != nil {
		http.Error(w, "Error processing request", http.StatusInternalServerError)
		return
	}

	m.ID = uuid.New().String()
	_, err = db.Exec("INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)", m.ID, m.Email, m.Name, string(hashedPassword))
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func loginMerchant(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var m Merchant
	err := json.NewDecoder(r.Body).Decode(&m)
	if err != nil || m.Email == "" || m.Password == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	var storedPassword string
	err = db.QueryRow("SELECT password FROM merchants WHERE email = ?", m.Email).Scan(&storedPassword)
	if err != nil {
		http.Error(w, "Invalid email or password", http.StatusUnauthorized)
		return
	}

	err = bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(m.Password))
	if err != nil {
		http.Error(w, "Invalid email or password", http.StatusUnauthorized)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "AUTH_COOKIE",
		Value:    m.Email,
		Path:     "/",
		HttpOnly: true,
		Secure:   false, // Set to true in production
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

	var m Merchant
	err = db.QueryRow("SELECT id FROM merchants WHERE email = ?", cookie.Value).Scan(&m.ID)
	if err != nil {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	var input struct {
		CSV string `json:"csv"`
	}
	err = json.NewDecoder(r.Body).Decode(&input)
	if err != nil || input.CSV == "" {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	rdr := csv.NewReader(strings.NewReader(input.CSV))
	records, err := rdr.ReadAll()
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

		_, err = db.Exec("INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)", record[0], record[1], price, m.ID)
		if err != nil {
			http.Error(w, "Error processing request", http.StatusInternalServerError)
			return
		}
	}

	w.WriteHeader(http.StatusOK)
}

func getWares(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

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

	w.Header().Set("Content-Type", "text/html")
	fmt.Fprintln(w, "<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>")
	for rows.Next() {
		var name, description, email string
		var price float64
		err := rows.Scan(&name, &description, &price, &email)
		if err != nil {
			http.Error(w, "Error processing request", http.StatusInternalServerError)
			return
		}
		fmt.Fprintf(w, "<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>", name, description, price, email)
	}
	fmt.Fprintln(w, "</table>")
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/merchants/register", registerMerchant)
	http.HandleFunc("/merchants/login", loginMerchant)
	http.HandleFunc("/merchants/upload-wares", uploadWares)
	http.HandleFunc("/wares", getWares)

	log.Fatal(http.ListenAndServe("0.0.0.0:5000", nil))
}