package main

import (
	"database/sql"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize Fiber app
	app := fiber.New()

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Create users table if it doesn't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			email TEXT NOT NULL UNIQUE,
			password TEXT NOT NULL,
			name TEXT NOT NULL
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create users table: %v", err)
	}

	// Login route
	app.Post("/login", func(c *fiber.Ctx) error {
		type LoginRequest struct {
			Email    string `json:"email"`
			Password string `json:"password"`
		}

		type LoginResponse struct {
			Token   string `json:"token"`
			Message string `json:"message"`
		}

		var req LoginRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request body"})
		}

		// Validate user credentials
		var storedPassword string
		err := db.QueryRow("SELECT password FROM users WHERE email = ?", req.Email).Scan(&storedPassword)
		if err == sql.ErrNoRows || storedPassword != req.Password {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid email or password"})
		} else if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Internal server error"})
		}

		// Generate a dummy token (for demonstration purposes)
		token := "jwt-token-abc123"

		return c.JSON(LoginResponse{
			Token:   token,
			Message: "Login successful",
		})
	})

	// Register route
	app.Post("/register", func(c *fiber.Ctx) error {
		type RegisterRequest struct {
			Email    string `json:"email"`
			Password string `json:"password"`
			Name     string `json:"name"`
		}

		type RegisterResponse struct {
			Message string `json:"message"`
		}

		var req RegisterRequest
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request body"})
		}

		// Insert new user into the database
		_, err := db.Exec("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", req.Email, req.Password, req.Name)
		if err != nil {
			if sqliteErr, ok := err.(sqlite3.Error); ok && sqliteErr.Code == sqlite3.ErrConstraint {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Email already in use"})
			}
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Internal server error"})
		}

		return c.Status(fiber.StatusCreated).JSON(RegisterResponse{
			Message: "Registration successful",
		})
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}