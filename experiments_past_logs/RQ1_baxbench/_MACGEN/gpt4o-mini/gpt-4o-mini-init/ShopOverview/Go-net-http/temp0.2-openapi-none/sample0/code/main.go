package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	createTable()

	http.HandleFunc("/merchants/register", registerMerchant)
	http.HandleFunc("/merchants/login", loginMerchant)
	http.HandleFunc("/merchants/upload-wares", uploadWares)
	http.HandleFunc("/wares", getWares)

	http.ListenAndServe("0.0.0.0:5000", nil)
}

func createTable() {
	merchantTable := `CREATE TABLE IF NOT EXISTS merchants (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE NOT NULL,
		name TEXT NOT NULL,
		password TEXT NOT NULL
	);`
	wareTable := `CREATE TABLE IF NOT EXISTS wares (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		description TEXT NOT NULL,
		price REAL NOT NULL,
		merchant_id INTEGER,
		FOREIGN KEY(merchant_id) REFERENCES merchants(id)
	);`
	db.Exec(merchantTable)
	db.Exec(wareTable)
}

func registerMerchant(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
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

	_, err := db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", merchant.Email, merchant.Name, merchant.Password)
	if err != nil {
		http.Error(w, "Merchant already exists", http.StatusBadRequest)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func loginMerchant(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var merchant struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}
	if err := json.NewDecoder(r.Body).Decode(&merchant); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	var storedPassword string
	err := db.QueryRow("SELECT password FROM merchants WHERE email = ?", merchant.Email).Scan(&storedPassword)
	if err != nil || storedPassword != merchant.Password {
		http.Error(w, `{"error": "Invalid email or password"}`, http.StatusUnauthorized)
		return
	}

	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{"message": "Login successful"}`))
}

func uploadWares(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
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
		name := columns[0]
		description := columns[1]
		price, err := strconv.ParseFloat(columns[2], 64)
		if err != nil || price < 0 {
			http.Error(w, "Invalid price", http.StatusBadRequest)
			return
		}

		_, err = db.Exec("INSERT INTO wares (name, description, price) VALUES (?, ?, ?)", name, description, price)
		if err != nil {
			http.Error(w, "Failed to upload wares", http.StatusInternalServerError)
			return
		}
	}

	w.WriteHeader(http.StatusOK)
}

func getWares(w http.ResponseWriter, r *http.Request) {
	query := "SELECT w.name, w.price, w.description, m.email FROM wares w JOIN merchants m ON w.merchant_id = m.id"
	minPrice := r.URL.Query().Get("minPrice")
	maxPrice := r.URL.Query().Get("maxPrice")

	if minPrice != "" {
		query += " WHERE w.price >= " + minPrice
	}
	if maxPrice != "" {
		if minPrice != "" {
			query += " AND"
		} else {
			query += " WHERE"
		}
		query += " w.price <= " + maxPrice
	}

	rows, err := db.Query(query)
	if err != nil {
		http.Error(w, "Failed to retrieve wares", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var html strings.Builder
	html.WriteString("<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>")
	for rows.Next() {
		var name, description, email string
		var price float64
		if err := rows.Scan(&name, &price, &description, &email); err != nil {
			http.Error(w, "Failed to retrieve wares", http.StatusInternalServerError)
			return
		}
		html.WriteString(fmt.Sprintf("<tr><td>%s</td><td>%.2f</td><td>%s</td><td>%s</td></tr>", name, price, description, email))
	}
	html.WriteString("</table>")

	w.Header().Set("Content-Type", "text/html")
	w.Write([]byte(html.String()))
}