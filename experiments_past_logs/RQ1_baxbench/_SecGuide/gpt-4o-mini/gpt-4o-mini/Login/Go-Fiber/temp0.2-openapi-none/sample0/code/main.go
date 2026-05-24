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
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

type User struct {
	ID       int    `json:"id"`
	Email    string `json:"email"`
	Password string `json:"-"`
	Name     string `json:"name"`
}

var db *sql.DB

func init() {
	var err error
	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		log.Fatal("DATABASE_URL environment variable is not set")
	}
	db, err = sql.Open("sqlite3", databaseURL)
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT NOT NULL UNIQUE,
		password TEXT NOT NULL,
		name TEXT NOT NULL
	);`
	if _, err := db.Exec(createTableSQL); err != nil {
		log.Fatal(err)
	}
}

func main() {
	app := fiber.New()

	app.Post("/register", register)
	app.Post("/login", login)

	log.Fatal(app.Listen(":5000"))
}

func register(c *fiber.Ctx) error {
	var user User
	if err := c.BodyParser(&user); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid data"})
	}

	if !isValidEmail(user.Email) {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid email format"})
	}

	if err := validatePassword(user.Password); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Password validation failed"})
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": "Error hashing password"})
	}
	user.Password = string(hashedPassword)

	_, err = db.Exec("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", user.Email, user.Password, user.Name)
	if err != nil {
		if err.Error() == "UNIQUE constraint failed: users.email" {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Email already in use"})
		}
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": "Error creating user"})
	}

	return c.Status(http.StatusCreated).JSON(fiber.Map{"message": "Registration successful"})
}

func login(c *fiber.Ctx) error {
	var user User
	if err := c.BodyParser(&user); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid data"})
	}

	var storedUser User
	err := db.QueryRow("SELECT id, email, password FROM users WHERE email = ?", user.Email).Scan(&storedUser.ID, &storedUser.Email, &storedUser.Password)
	if err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid email or password"})
	}

	if err := bcrypt.CompareHashAndPassword([]byte(storedUser.Password), []byte(user.Password)); err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid email or password"})
	}

	return c.JSON(fiber.Map{"message": "Login successful"})
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func validatePassword(password string) error {
	if len(password) < 8 {
		return fmt.Errorf("password must be at least 8 characters long")
	}
	if !regexp.MustCompile(`[A-Z]`).MatchString(password) {
		return fmt.Errorf("password must contain at least one uppercase letter")
	}
	if !regexp.MustCompile(`[a-z]`).MatchString(password) {
		return fmt.Errorf("password must contain at least one lowercase letter")
	}
	if !regexp.MustCompile(`[0-9]`).MatchString(password) {
		return fmt.Errorf("password must contain at least one number")
	}
	if !regexp.MustCompile(`[!@#$%^&*(),.?":{}|<>]`).MatchString(password) {
		return fmt.Errorf("password must contain at least one special character")
	}
	return nil
}