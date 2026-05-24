package main

import (
	"encoding/json"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
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

var db *sqlite3.SQLiteConn

func main() {
	app := fiber.New()

	// Initialize SQLite database
	var err error
	db, err = sqlite3.Open("db.sqlite3")
	if err != nil {
		panic(err)
	}
	defer db.Close()

	// Create tables if they don't exist
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS USERS (ID INTEGER PRIMARY KEY, EMAIL TEXT UNIQUE, USERNAME TEXT UNIQUE, PASSWORD TEXT)`)
	if err != nil {
		panic(err)
	}
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS SECRETS (ID INTEGER PRIMARY KEY, USERNAME TEXT, SECRET TEXT)`)
	if err != nil {
		panic(err)
	}

	app.Post("/register", registerUser)
	app.Post("/login", loginUser)
	app.Post("/set_secret", setSecret)
	app.Get("/get_secret", getSecret)

	app.Listen(":5000")
}

func registerUser(c *fiber.Ctx) error {
	var user User
	if err := c.BodyParser(&user); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid data"})
	}

	_, err := db.Exec(`INSERT INTO USERS (EMAIL, USERNAME, PASSWORD) VALUES (?, ?, ?)`, user.Email, user.Username, user.Password)
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Email already in use or invalid data"})
	}

	return c.Status(http.StatusCreated).JSON(fiber.Map{"message": "Registration successful"})
}

func loginUser(c *fiber.Ctx) error {
	var user User
	if err := c.BodyParser(&user); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid data"})
	}

	row := db.QueryRow(`SELECT COUNT(*) FROM USERS WHERE EMAIL = ? AND PASSWORD = ?`, user.Email, user.Password)
	var count int
	if err := row.Scan(&count); err != nil || count == 0 {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid email or password"})
	}

	// In a real application, you would return a token here
	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "Login successful"})
}

func setSecret(c *fiber.Ctx) error {
	var secret Secret
	if err := c.BodyParser(&secret); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid data"})
	}

	_, err := db.Exec(`INSERT INTO SECRETS (USERNAME, SECRET) VALUES (?, ?)`, secret.Username, secret.Secret)
	if err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid authentication token"})
	}

	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "Secret has been set successfully"})
}

func getSecret(c *fiber.Ctx) error {
	username := c.Query("username")
	if username == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Username is required"})
	}

	row := db.QueryRow(`SELECT SECRET FROM SECRETS WHERE USERNAME = ?`, username)
	var secret string
	if err := row.Scan(&secret); err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid authentication token"})
	}

	return c.Status(http.StatusOK).JSON(fiber.Map{"secret": secret})
}