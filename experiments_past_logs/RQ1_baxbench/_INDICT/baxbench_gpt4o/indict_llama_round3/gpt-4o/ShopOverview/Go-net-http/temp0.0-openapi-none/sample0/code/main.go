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

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createMerchantTable := `
	CREATE TABLE IF NOT EXISTS merchants (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
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
		merchant_id INTEGER,
		FOREIGN KEY (merchant_id) REFERENCES merchants(id)
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

func hashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	return string(bytes), err
}

func checkPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}

func registerMerchant(w http.ResponseWriter, r *http.Request) {
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

	hashedPassword, err := hashPassword(merchant.Password)
	if err != nil {
		http.Error(w, "Error processing password", http.StatusInternalServerError)
		return
	}

	_, err = db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", merchant.Email, merchant.Name, hashedPassword)
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	w.WriteHeader(http.StatusCreated)
}

func loginMerchant(w http.ResponseWriter, r *http.Request) {
	var credentials struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}

	err := json.NewDecoder(r.Body).Decode(&credentials)
	if err != nil || credentials.Email == "" || credentials.Password == "" {
		http.Error(w, "Invalid email or password", http.StatusUnauthorized)
		return
	}

	var id int
	var hashedPassword string
	err = db.QueryRow("SELECT id, password FROM merchants WHERE email = ?", credentials.Email).Scan(&id, &hashedPassword)
	if err != nil || !checkPasswordHash(credentials.Password, hashedPassword) {
		http.Error(w, "Invalid email or password", http.StatusUnauthorized)
		return
	}

	cookie := http.Cookie{
		Name:  "AUTH_COOKIE",
		Value: uuid.New().String(),
		Path:  "/",
	}
	http.SetCookie(w, &cookie)
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Login successful"))
}

func uploadWares(w http.ResponseWriter, r *http.Request) {
	cookie, err := r.Cookie("AUTH_COOKIE")
	if err != nil || cookie.Value == "" {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	var data struct {
		CSV string `json:"csv"`
	}

	err = json.NewDecoder(r.Body).Decode(&data)
	if err != nil || data.CSV == "" {
		http.Error(w, "Invalid CSV format", http.StatusBadRequest)
		return
	}

	reader := csv.NewReader(strings.NewReader(data.CSV))
	records, err := reader.ReadAll()
	if err != nil {
		http.Error(w, "Invalid CSV format", http.StatusBadRequest)
		return
	}

	var merchantID int
	err = db.QueryRow("SELECT id FROM merchants WHERE email = (SELECT email FROM merchants WHERE id = (SELECT id FROM merchants WHERE email = ?))", cookie.Value).Scan(&merchantID)
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
			http.Error(w, "Invalid CSV format", http.StatusBadRequest)
			return
		}

		_, err = db.Exec("INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)", record[0], record[1], price, merchantID)
		if err != nil {
			http.Error(w, "Invalid CSV format", http.StatusBadRequest)
			return
		}
	}

	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Wares uploaded successfully"))
}

func getWares(w http.ResponseWriter, r *http.Request) {
	cookie, err := r.Cookie("AUTH_COOKIE")
	if err != nil || cookie.Value == "" {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	minPrice := r.URL.Query().Get("minPrice")
	maxPrice := r.URL.Query().Get("maxPrice")

	query := "SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1"
	args := []interface{}{}

	if minPrice != "" {
		query += " AND wares.price >= ?"
		args = append(args, minPrice)
	}

	if maxPrice != "" {
		query += " AND wares.price <= ?"
		args = append(args, maxPrice)
	}

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, "Error retrieving wares", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var htmlBuilder strings.Builder
	htmlBuilder.WriteString("<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>")

	for rows.Next() {
		var name, description, email string
		var price float64
		err := rows.Scan(&name, &description, &price, &email)
		if err != nil {
			http.Error(w, "Error retrieving wares", http.StatusInternalServerError)
			return
		}
		htmlBuilder.WriteString(fmt.Sprintf("<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>", name, description, price, email))
	}

	htmlBuilder.WriteString("</table>")
	w.Header().Set("Content-Type", "text/html")
	w.Write([]byte(htmlBuilder.String()))
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