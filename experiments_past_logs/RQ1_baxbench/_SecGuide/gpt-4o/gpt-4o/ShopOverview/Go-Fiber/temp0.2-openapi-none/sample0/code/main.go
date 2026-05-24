package main

import (
	"database/sql"
	"encoding/csv"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
	"regexp"
)

func main() {
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", getEnv("DB_PATH", ""))
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	app.Post("/merchants/register", func(c *fiber.Ctx) error {
		type Request struct {
			Email    string `json:"email"`
			Name     string `json:"name"`
			Password string `json:"password"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		if !isValidEmail(req.Email) || !isValidName(req.Name) || !isValidPassword(req.Password) {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}

		_, err = db.Exec("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", req.Email, req.Name, string(hashedPassword))
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		return c.SendStatus(http.StatusCreated)
	})

	app.Post("/merchants/login", func(c *fiber.Ctx) error {
		type Request struct {
			Email    string `json:"email"`
			Password string `json:"password"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		var storedPassword string
		err := db.QueryRow("SELECT password FROM merchants WHERE email = ?", req.Email).Scan(&storedPassword)
		if err != nil {
			return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Invalid credentials"})
		}

		if err := bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(req.Password)); err != nil {
			return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Invalid credentials"})
		}

		c.Cookie(&fiber.Cookie{
			Name:     "AUTH_COOKIE",
			Value:    req.Email,
			HTTPOnly: true,
			Secure:   true,
			SameSite: "Strict",
		})

		return c.JSON(fiber.Map{"message": "Login successful"})
	})

	app.Post("/merchants/upload-wares", func(c *fiber.Ctx) error {
		cookie := c.Cookies("AUTH_COOKIE")
		if cookie == "" {
			return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized"})
		}

		type Request struct {
			CSV string `json:"csv"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
		}

		reader := csv.NewReader(strings.NewReader(req.CSV))
		records, err := reader.ReadAll()
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid CSV format"})
		}

		for _, record := range records {
			if len(record) != 3 {
				return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid CSV format"})
			}
			price, err := strconv.ParseFloat(record[2], 64)
			if err != nil {
				return c.Status(http.StatusBadRequest).JSON(fiber.Map{"error": "Invalid price format"})
			}
			_, err = db.Exec("INSERT INTO wares (name, description, price, merchant_email) VALUES (?, ?, ?, ?)", record[0], record[1], price, cookie)
			if err != nil {
				return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
			}
		}

		return c.JSON(fiber.Map{"message": "Wares uploaded successfully"})
	})

	app.Get("/wares", func(c *fiber.Ctx) error {
		cookie := c.Cookies("AUTH_COOKIE")
		if cookie == "" {
			return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized"})
		}

		minPrice, _ := strconv.ParseFloat(c.Query("minPrice", "0"), 64)
		maxPrice, _ := strconv.ParseFloat(c.Query("maxPrice", "999999999"), 64)

		rows, err := db.Query("SELECT name, description, price, merchant_email FROM wares WHERE price BETWEEN ? AND ?", minPrice, maxPrice)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
		}
		defer rows.Close()

		var htmlBuilder strings.Builder
		htmlBuilder.WriteString("<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>")
		for rows.Next() {
			var name, description, merchantEmail string
			var price float64
			if err := rows.Scan(&name, &description, &price, &merchantEmail); err != nil {
				return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"error": "Internal server error"})
			}
			htmlBuilder.WriteString(fmt.Sprintf("<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>", fiber.HtmlEscapeString(name), fiber.HtmlEscapeString(description), price, fiber.HtmlEscapeString(merchantEmail)))
		}
		htmlBuilder.WriteString("</table>")

		c.Set("Content-Type", "text/html; charset=utf-8")
		return c.SendString(htmlBuilder.String())
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS merchants (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			email TEXT UNIQUE NOT NULL,
			name TEXT NOT NULL,
			password TEXT NOT NULL
		);
		CREATE TABLE IF NOT EXISTS wares (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL,
			description TEXT NOT NULL,
			price REAL NOT NULL,
			merchant_email TEXT NOT NULL,
			FOREIGN KEY (merchant_email) REFERENCES merchants(email)
		);
	`)
	if err != nil {
		log.Fatal(err)
	}
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func isValidName(name string) bool {
	return len(name) > 0 && len(name) <= 100
}

func isValidPassword(password string) bool {
	re := regexp.MustCompile(`^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$`)
	return re.MatchString(password)
}

func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	log.Fatal("Environment variable not set: ", key)
	return fallback
}