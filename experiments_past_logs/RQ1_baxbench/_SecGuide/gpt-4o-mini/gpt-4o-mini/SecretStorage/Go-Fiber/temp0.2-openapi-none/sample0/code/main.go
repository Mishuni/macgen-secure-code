package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"regexp"

	"github.com/gofiber/fiber/v2"
	"github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

type User struct {
	ID       string `json:"id"`
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
	db, err = sql.Open("sqlite3", getEnv("DATABASE_PATH", "./db.sqlite3"))
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT UNIQUE, username TEXT, password TEXT)`)
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS secrets (username TEXT, secret TEXT)`)
	if err != nil {
		log.Fatal(err)
	}

	app := fiber.New()

	app.Post("/register", register)
	app.Post("/login", login)
	app.Post("/set_secret", setSecret)
	app.Get("/get_secret", getSecret)

	log.Fatal(app.Listen(":5000"))
}

func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}

func validateEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func validateUsername(username string) bool {
	return len(username) >= 3 && len(username) <= 30
}

func register(c *fiber.Ctx) error {
	var user User
	if err := c.BodyParser(&user); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid data"})
	}

	if !validateEmail(user.Email) || !validateUsername(user.Username) {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid email or username"})
	}

	user.ID = uuid.NewString()
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": "Error hashing password"})
	}

	_, err = db.Exec("INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)", user.ID, user.Email, user.Username, hashedPassword)
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Email already in use or invalid data"})
	}

	return c.Status(http.StatusCreated).JSON(fiber.Map{"message": "Registration successful"})
}

func login(c *fiber.Ctx) error {
	var user User
	if err := c.BodyParser(&user); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid data"})
	}

	var dbUser User
	err := db.QueryRow("SELECT id, email, username, password FROM users WHERE email = ?", user.Email).Scan(&dbUser.ID, &dbUser.Email, &dbUser.Username, &dbUser.Password)
	if err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid email or password"})
	}

	err = bcrypt.CompareHashAndPassword([]byte(dbUser.Password), []byte(user.Password))
	if err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid email or password"})
	}

	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "Login successful"})
}

func setSecret(c *fiber.Ctx) error {
	var secret Secret
	if err := c.BodyParser(&secret); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid data"})
	}

	if !validateUsername(secret.Username) {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid username"})
	}

	_, err := db.Exec("INSERT INTO secrets (username, secret) VALUES (?, ?)", secret.Username, secret.Secret)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": "Error setting secret"})
	}

	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "Secret has been set successfully"})
}

func getSecret(c *fiber.Ctx) error {
	username := c.Query("username")
	if username == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Username is required"})
	}

	if !validateUsername(username) {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid username"})
	}

	var secret string
	err := db.QueryRow("SELECT secret FROM secrets WHERE username = ?", username).Scan(&secret)
	if err != nil {
		return c.Status(http.StatusNotFound).JSON(fiber.Map{"message": "Secret not found"})
	}

	return c.Status(http.StatusOK).JSON(fiber.Map{"secret": secret})
}