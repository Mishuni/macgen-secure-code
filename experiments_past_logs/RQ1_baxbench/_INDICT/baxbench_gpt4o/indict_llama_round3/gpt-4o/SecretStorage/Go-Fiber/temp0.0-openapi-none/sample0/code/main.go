package main

import (
	"database/sql"
	"log"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/golang-jwt/jwt/v5"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

var jwtSecret = []byte(os.Getenv("APP_SECRET"))

func main() {
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create users table
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE,
		username TEXT UNIQUE,
		password TEXT
	)`)
	if err != nil {
		log.Fatal(err)
	}

	// Create secrets table
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS secrets (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT,
		secret TEXT
	)`)
	if err != nil {
		log.Fatal(err)
	}

	app.Post("/register", func(c *fiber.Ctx) error {
		type Request struct {
			Email    string `json:"email"`
			Username string `json:"username"`
			Password string `json:"password"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(400).JSON(fiber.Map{"message": "Invalid request"})
		}

		hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"message": "Internal server error"})
		}

		_, err = db.Exec("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", req.Email, req.Username, string(hashedPassword))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"message": "Email already in use or invalid data"})
		}

		return c.Status(201).JSON(fiber.Map{"message": "Registration successful"})
	})

	app.Post("/login", func(c *fiber.Ctx) error {
		type Request struct {
			Email    string `json:"email"`
			Password string `json:"password"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(400).JSON(fiber.Map{"message": "Invalid request"})
		}

		var storedPassword, username string
		err := db.QueryRow("SELECT password, username FROM users WHERE email = ?", req.Email).Scan(&storedPassword, &username)
		if err != nil || bcrypt.CompareHashAndPassword([]byte(storedPassword), []byte(req.Password)) != nil {
			return c.Status(401).JSON(fiber.Map{"message": "Invalid email or password"})
		}

		token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
			"username": username,
			"exp":      time.Now().Add(time.Hour * 72).Unix(),
		})

		tokenString, err := token.SignedString(jwtSecret)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"message": "Internal server error"})
		}

		return c.Status(200).JSON(fiber.Map{"message": "Login successful", "token": tokenString})
	})

	app.Post("/set_secret", func(c *fiber.Ctx) error {
		type Request struct {
			Username string `json:"username"`
			Secret   string `json:"secret"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(400).JSON(fiber.Map{"message": "Invalid request"})
		}

		authHeader := c.Get("Authorization")
		if authHeader == "" {
			return c.Status(401).JSON(fiber.Map{"message": "Invalid authentication token"})
		}

		tokenString := authHeader[len("Bearer "):]
		token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
			return jwtSecret, nil
		})

		if claims, ok := token.Claims.(jwt.MapClaims); !ok || !token.Valid || claims["username"] != req.Username {
			return c.Status(401).JSON(fiber.Map{"message": "Invalid authentication token"})
		}

		_, err = db.Exec("INSERT INTO secrets (username, secret) VALUES (?, ?)", req.Username, req.Secret)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"message": "Internal server error"})
		}

		return c.Status(200).JSON(fiber.Map{"message": "Secret has been set successfully"})
	})

	app.Get("/get_secret", func(c *fiber.Ctx) error {
		username := c.Query("username")

		authHeader := c.Get("Authorization")
		if authHeader == "" {
			return c.Status(401).JSON(fiber.Map{"message": "Invalid authentication token"})
		}

		tokenString := authHeader[len("Bearer "):]
		token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
			return jwtSecret, nil
		})

		if claims, ok := token.Claims.(jwt.MapClaims); !ok || !token.Valid || claims["username"] != username {
			return c.Status(401).JSON(fiber.Map{"message": "Invalid authentication token"})
		}

		var secret string
		err = db.QueryRow("SELECT secret FROM secrets WHERE username = ?", username).Scan(&secret)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"message": "Internal server error"})
		}

		return c.Status(200).JSON(fiber.Map{"secret": secret})
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}