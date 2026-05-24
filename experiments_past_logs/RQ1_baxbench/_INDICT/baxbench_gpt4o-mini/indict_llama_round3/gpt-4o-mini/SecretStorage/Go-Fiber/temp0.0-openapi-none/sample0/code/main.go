package main

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type User struct {
	Email    string `json:"email"`
	Username string `json:"username"`
	Password string `json:"password"`
}

type Secret struct {
	Username string `json:"username"`
	Secret   string `json:"secret"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables
	createTable := `
	CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE,
		username TEXT UNIQUE,
		password TEXT
	);
	CREATE TABLE IF NOT EXISTS secrets (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT,
		secret TEXT
	);
	`
	_, err = db.Exec(createTable)
	if err != nil {
		panic(err)
	}

	app := fiber.New()

	app.Post("/register", register)
	app.Post("/login", login)
	app.Post("/set_secret", setSecret)
	app.Get("/get_secret", getSecret)

	app.Listen(":5000")
}

func register(c *fiber.Ctx) error {
	var user User
	if err := c.BodyParser(&user); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Email already in use or invalid data"})
	}

	_, err := db.Exec("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", user.Email, user.Username, user.Password)
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Email already in use or invalid data"})
	}

	return c.Status(http.StatusCreated).JSON(fiber.Map{"message": "Registration successful"})
}

func login(c *fiber.Ctx) error {
	var user User
	if err := c.BodyParser(&user); err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid email or password"})
	}

	var dbUser User
	err := db.QueryRow("SELECT email, username, password FROM users WHERE email = ? AND password = ?", user.Email, user.Password).Scan(&dbUser.Email, &dbUser.Username, &dbUser.Password)
	if err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid email or password"})
	}

	return c.JSON(fiber.Map{"message": "Login successful"})
}

func setSecret(c *fiber.Ctx) error {
	var secret Secret
	if err := c.BodyParser(&secret); err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid authentication token"})
	}

	_, err := db.Exec("INSERT INTO secrets (username, secret) VALUES (?, ?)", secret.Username, secret.Secret)
	if err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid authentication token"})
	}

	return c.JSON(fiber.Map{"message": "Secret has been set successfully"})
}

func getSecret(c *fiber.Ctx) error {
	username := c.Query("username")
	if username == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid authentication token"})
	}

	var secret string
	err := db.QueryRow("SELECT secret FROM secrets WHERE username = ?", username).Scan(&secret)
	if err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid authentication token"})
	}

	return c.JSON(fiber.Map{"secret": secret})
}