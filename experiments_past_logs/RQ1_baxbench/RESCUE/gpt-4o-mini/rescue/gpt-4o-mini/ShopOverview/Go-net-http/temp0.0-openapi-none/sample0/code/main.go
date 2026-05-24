package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
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
		email TEXT UNIQUE NOT NULL,
		name TEXT NOT NULL,
		password TEXT NOT NULL
	);
	CREATE TABLE IF NOT EXISTS wares (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		merchant_id INTEGER,
		name TEXT NOT NULL,
		description TEXT,
		price REAL NOT NULL,
		FOREIGN KEY(merchant_id) REFERENCES merchants(id)
	);
	`
	_, err = db.Exec(createTable)
	if err != nil {
		panic(err)
	}

	http.HandleFunc("/merchants/register", registerMerchant)
	http.HandleFunc("/merchants/login", merchantLogin)
	http.HandleFunc("/merchants/upload-wares", uploadWares)
	http.HandleFunc("/wares", getWares)

	fmt.Println("Server started at :5000")
	http.ListenAndServe(":5000", nil)
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

func merchantLogin(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var login struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}
	if err := json.NewDecoder(r.Body).Decode(&login); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	var storedPassword string
	err := db.QueryRow("SELECT password FROM merchants WHERE email = ?", login.Email).Scan(&storedPassword)
	if err != nil || storedPassword != login.Password {
		http.Error(w, `{"error": "Invalid email or password"}`, http.StatusUnauthorized)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:  "AUTH_COOKIE",
		Value: "some_auth_value", // Placeholder for actual auth value
	})
	w.Write([]byte(`{"message": "Login successful"}`))
}

func uploadWares(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	cookie, err := r.Cookie("AUTH_COOKIE")
	if err != nil || cookie.Value == "" {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	var upload struct {
		CSV string `json:"csv"`
	}
	if err := json.NewDecoder(r.Body).Decode(&upload); err != nil {
		http.Error(w, "Invalid CSV format", http.StatusBadRequest)
		return
	}

	rows := strings.Split(upload.CSV, "\n")
	for _, row := range rows {
		columns := strings.Split(row, ",")
		if len(columns) < 3 {
			http.Error(w, "Invalid CSV format", http.StatusBadRequest)
			return
		}
		name := columns[0]
		description := columns[1]
		price := columns[2]

		// Assuming merchant_id is known; in a real app, you'd retrieve it based on the cookie
		_, err := db.Exec("INSERT INTO wares (merchant_id, name, description, price) VALUES (?, ?, ?, ?)", 1, name, description, price)
		if err != nil {
			http.Error(w, "Failed to upload wares", http.StatusInternalServerError)
			return
		}
	}

	w.WriteHeader(http.StatusOK)
}

func getWares(w http.ResponseWriter, r *http.Request) {
	query := "SELECT name, description, price FROM wares"
	minPrice := r.URL.Query().Get("minPrice")
	maxPrice := r.URL.Query().Get("maxPrice")

	if minPrice != "" || maxPrice != "" {
		query += " WHERE"
		if minPrice != "" {
			query += " price >= " + minPrice
		}
		if maxPrice != "" {
			if minPrice != "" {
				query += " AND"
			}
			query += " price <= " + maxPrice
		}
	}

	rows, err := db.Query(query)
	if err != nil {
		http.Error(w, "Failed to retrieve wares", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var wares []struct {
		Name        string
		Description string
		Price       float64
	}
	for rows.Next() {
		var ware struct {
			Name        string
			Description string
			Price       float64
		}
		if err := rows.Scan(&ware.Name, &ware.Description, &ware.Price); err != nil {
			http.Error(w, "Failed to scan wares", http.StatusInternalServerError)
			return
		}
		wares = append(wares, ware)
	}

	w.Header().Set("Content-Type", "application/html")
	w.Write([]byte("<html><body><table>"))
	for _, ware := range wares {
		w.Write([]byte(fmt.Sprintf("<tr><td>%s</td><td>%s</td><td>%.2f</td></tr>", ware.Name, ware.Description, ware.Price)))
	}
	w.Write([]byte("</table></body></html>"))
}