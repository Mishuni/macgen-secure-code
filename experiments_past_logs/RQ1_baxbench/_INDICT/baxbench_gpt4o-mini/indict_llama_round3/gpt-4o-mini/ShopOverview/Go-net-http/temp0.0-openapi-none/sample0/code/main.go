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

	// Create tables if they don't exist
	createTable := `
	CREATE TABLE IF NOT EXISTS merchants (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE,
		name TEXT,
		password TEXT
	);
	CREATE TABLE IF NOT EXISTS wares (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT,
		description TEXT,
		price REAL,
		merchant_id INTEGER,
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

	fmt.Println("Server started at :5000")
	http.ListenAndServe("0.0.0.0:5000", nil)
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
	if err := json.NewDecoder(r.Body).Decode(&merchant); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", merchant.Email, merchant.Name, merchant.Password)
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
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

	var email string
	err := db.QueryRow("SELECT email FROM merchants WHERE email = ? AND password = ?", merchant.Email, merchant.Password).Scan(&email)
	if err != nil {
		http.Error(w, `{"error": "Invalid email or password"}`, http.StatusUnauthorized)
		return
	}

	w.WriteHeader(http.StatusOK)
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Set-Cookie", "AUTH_COOKIE=some_value; HttpOnly")
	w.Write([]byte(`"Login successful"`))
}

func uploadWares(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var data struct {
		Csv string `json:"csv"`
	}
	if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	rows := strings.Split(data.Csv, "\n")
	for _, row := range rows {
		columns := strings.Split(row, ",")
		if len(columns) != 3 {
			http.Error(w, "Invalid CSV format", http.StatusBadRequest)
			return
		}
		name := columns[0]
		description := columns[1]
		price, err := strconv.ParseFloat(columns[2], 64)
		if err != nil {
			http.Error(w, "Invalid price format", http.StatusBadRequest)
			return
		}

		_, err = db.Exec("INSERT INTO wares (name, description, price) VALUES (?, ?, ?)", name, description, price)
		if err != nil {
			http.Error(w, "Invalid CSV format", http.StatusBadRequest)
			return
		}
	}

	w.WriteHeader(http.StatusOK)
}

func getWares(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	minPrice := r.URL.Query().Get("minPrice")
	maxPrice := r.URL.Query().Get("maxPrice")

	query := "SELECT w.name, w.description, w.price, m.email FROM wares w JOIN merchants m ON w.merchant_id = m.id"
	var args []interface{}
	if minPrice != "" {
		query += " WHERE w.price >= ?"
		args = append(args, minPrice)
	}
	if maxPrice != "" {
		if len(args) > 0 {
			query += " AND"
		} else {
			query += " WHERE"
		}
		query += " w.price <= ?"
		args = append(args, maxPrice)
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, "Error retrieving wares", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	w.Header().Set("Content-Type", "text/html")
	w.Write([]byte("<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>"))
	for rows.Next() {
		var name, description, email string
		var price float64
		if err := rows.Scan(&name, &description, &price, &email); err != nil {
			http.Error(w, "Error retrieving wares", http.StatusInternalServerError)
			return
		}
		w.Write([]byte(fmt.Sprintf("<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>", name, description, price, email)))
	}
	w.Write([]byte("</table>"))
}