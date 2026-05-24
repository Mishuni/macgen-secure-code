package main

import (
	"database/sql"
	"net/http"
	"os"
	"regexp"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

var db *sql.DB

type User struct {
	Email    string `json:"email"`
	Username string `json:"username"`
	Password string `json:"password"`
}

type Secret struct {
	Username string `json:"username"`
	Secret   string `json:"secret"`
}

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE,
		username TEXT UNIQUE,
		password TEXT
	);`)
	if err != nil {
		panic(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS secrets (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT,
		secret TEXT
	);`)
	if err != nil {
		panic(err)
	}
}

func main() {
	defer db.Close()

	app := fiber.New()

	app.Post("/register", func(c *fiber.Ctx) error {
		var user User
		if err := c.BodyParser(&user); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Email already in use or invalid data"})
		}

		if !isValidEmail(user.Email) || len(user.Password) < 6 {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Email already in use or invalid data"})
		}

		_, err := db.Exec("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", user.Email, user.Username, user.Password)
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Email already in use or invalid data"})
		}

		return c.Status(http.StatusCreated).JSON(fiber.Map{"message": "Registration successful"})
	})

	app.Post("/login", func(c *fiber.Ctx) error {
		var user User
		if err := c.BodyParser(&user); err != nil {
			return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid email or password"})
		}

		var dbUser User
		err := db.QueryRow("SELECT email, username, password FROM users WHERE email = ? AND password = ?", user.Email, user.Password).Scan(&dbUser.Email, &dbUser.Username, &dbUser.Password)
		if err != nil {
			return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid email or password"})
		}

		token := uuid.New().String() // Dummy token for demonstration
		return c.JSON(fiber.Map{"token": token, "message": "Login successful"})
	})

	app.Post("/set_secret", func(c *fiber.Ctx) error {
		var secret Secret
		if err := c.BodyParser(&secret); err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid username or secret"})
		}

		if secret.Username == "" || secret.Secret == "" {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid username or secret"})
		}

		_, err := db.Exec("INSERT INTO secrets (username, secret) VALUES (?, ?)", secret.Username, secret.Secret)
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid username or secret"})
		}

		return c.JSON(fiber.Map{"message": "Secret has been set successfully"})
	})

	app.Get("/get_secret", func(c *fiber.Ctx) error {
		username := c.Query("username")
		if username == "" {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid username"})
		}

		var secret string
		err := db.QueryRow("SELECT secret FROM secrets WHERE username = ?", username).Scan(&secret)
		if err != nil {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid username"})
		}

		return c.JSON(fiber.Map{"secret": secret})
	})

	app.Listen(":5000")
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}