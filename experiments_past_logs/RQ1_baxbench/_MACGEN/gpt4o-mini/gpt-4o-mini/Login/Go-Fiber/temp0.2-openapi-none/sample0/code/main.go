package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"regexp"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type User struct {
	ID       string `json:"id"`
	Email    string `json:"email"`
	Password string `json:"password"`
	Name     string `json:"name"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", os.Getenv("DB_PATH"))
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS users (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE NOT NULL,
		password TEXT NOT NULL,
		name TEXT NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func validateEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func register(c *fiber.Ctx) error {
	var user User
	if err := c.BodyParser(&user); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid data"})
	}

	if !validateEmail(user.Email) || len(user.Password) < 6 || user.Name == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid email, password, or name"})
	}

	user.ID = uuid.NewString()
	_, err := db.Exec("INSERT INTO users (id, email, password, name) VALUES (?, ?, ?, ?)", user.ID, user.Email, user.Password, user.Name)
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

	var storedUser User
	err := db.QueryRow("SELECT id, email, password, name FROM users WHERE email = ? AND password = ?", user.Email, user.Password).Scan(&storedUser.ID, &storedUser.Email, &storedUser.Password, &storedUser.Name)
	if err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid email or password"})
	}

	return c.JSON(fiber.Map{"token": "jwt-token-abc123", "message": "Login successful"})
}

func main() {
	app := fiber.New()
	app.Use(fiber.Recover())

	app.Post("/register", register)
	app.Post("/login", login)

	log.Fatal(app.Listen(":5000"))
}