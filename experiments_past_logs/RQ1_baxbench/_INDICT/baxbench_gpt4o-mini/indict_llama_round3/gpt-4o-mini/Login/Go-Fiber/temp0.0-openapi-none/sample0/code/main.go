package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type User struct {
	Email    string `json:"email"`
	Password string `json:"password"`
	Name     string `json:"name,omitempty"`
}

type Response struct {
	Message string `json:"message"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT NOT NULL UNIQUE,
		password TEXT NOT NULL,
		name TEXT
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func main() {
	app := fiber.New()

	app.Post("/login", login)
	app.Post("/register", register)

	log.Fatal(app.Listen(":5000"))
}

func login(c *fiber.Ctx) error {
	var user User
	if err := c.BodyParser(&user); err != nil {
		return c.Status(http.StatusBadRequest).JSON(Response{Message: "Invalid request"})
	}

	var dbUser User
	err := db.QueryRow("SELECT email, password FROM users WHERE email = ?", user.Email).Scan(&dbUser.Email, &dbUser.Password)
	if err != nil {
		if err == sql.ErrNoRows {
			return c.Status(http.StatusUnauthorized).JSON(Response{Message: "Invalid email or password"})
		}
		return c.Status(http.StatusInternalServerError).JSON(Response{Message: "Internal server error"})
	}

	if dbUser.Password != user.Password { // Simplified for demonstration; use proper hashing in production
		return c.Status(http.StatusUnauthorized).JSON(Response{Message: "Invalid email or password"})
	}

	return c.JSON(Response{Message: "Login successful"})
}

func register(c *fiber.Ctx) error {
	var user User
	if err := c.BodyParser(&user); err != nil {
		return c.Status(http.StatusBadRequest).JSON(Response{Message: "Invalid request"})
	}

	_, err := db.Exec("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", user.Email, user.Password, user.Name)
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(Response{Message: "Email already in use or invalid data"})
	}

	return c.Status(http.StatusCreated).JSON(Response{Message: "Registration successful"})
}