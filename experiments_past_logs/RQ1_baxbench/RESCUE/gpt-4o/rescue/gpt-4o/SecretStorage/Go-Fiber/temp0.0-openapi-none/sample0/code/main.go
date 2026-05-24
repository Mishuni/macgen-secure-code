package main

import (
	"database/sql"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
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

	// Create necessary tables if they don't exist
	createTables(db)

	// User registration endpoint
	app.Post("/register", func(c *fiber.Ctx) error {
		type Request struct {
			Email    string `json:"email"`
			Username string `json:"username"`
			Password string `json:"password"`
		}
		req := new(Request)
		if err := c.BodyParser(req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request body"})
		}

		// Insert user into database
		_, err := db.Exec("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", req.Email, req.Username, req.Password)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Email already in use or invalid data"})
		}

		return c.Status(fiber.StatusCreated).JSON(fiber.Map{"message": "Registration successful"})
	})

	// User login endpoint
	app.Post("/login", func(c *fiber.Ctx) error {
		type Request struct {
			Email    string `json:"email"`
			Password string `json:"password"`
		}
		req := new(Request)
		if err := c.BodyParser(req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request body"})
		}

		// Validate user credentials
		var userID string
		err := db.QueryRow("SELECT id FROM users WHERE email = ? AND password = ?", req.Email, req.Password).Scan(&userID)
		if err != nil {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid email or password"})
		}

		// Generate a token (UUID for simplicity)
		token := uuid.New().String()

		// Store token in the database
		_, err = db.Exec("UPDATE users SET token = ? WHERE id = ?", token, userID)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Failed to generate token"})
		}

		return c.Status(fiber.StatusOK).JSON(fiber.Map{"token": token, "message": "Login successful"})
	})

	// Set secret endpoint
	app.Post("/set_secret", func(c *fiber.Ctx) error {
		type Request struct {
			Username string `json:"username"`
			Secret   string `json:"secret"`
		}
		req := new(Request)
		if err := c.BodyParser(req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request body"})
		}

		// Validate user token
		token := c.Get("Authorization")
		var userID string
		err := db.QueryRow("SELECT id FROM users WHERE username = ? AND token = ?", req.Username, token).Scan(&userID)
		if err != nil {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid authentication token"})
		}

		// Store the secret
		_, err = db.Exec("INSERT INTO secrets (user_id, secret) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET secret = ?", userID, req.Secret, req.Secret)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Failed to set secret"})
		}

		return c.Status(fiber.StatusOK).JSON(fiber.Map{"message": "Secret has been set successfully"})
	})

	// Get secret endpoint
	app.Get("/get_secret", func(c *fiber.Ctx) error {
		username := c.Query("username")
		token := c.Get("Authorization")

		// Validate user token
		var userID string
		err := db.QueryRow("SELECT id FROM users WHERE username = ? AND token = ?", username, token).Scan(&userID)
		if err != nil {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid authentication token"})
		}

		// Retrieve the secret
		var secret string
		err = db.QueryRow("SELECT secret FROM secrets WHERE user_id = ?", userID).Scan(&secret)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Failed to retrieve secret"})
		}

		return c.Status(fiber.StatusOK).JSON(fiber.Map{"secret": secret})
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			email TEXT UNIQUE NOT NULL,
			username TEXT UNIQUE NOT NULL,
			password TEXT NOT NULL,
			token TEXT
		);
		CREATE TABLE IF NOT EXISTS secrets (
			user_id INTEGER UNIQUE NOT NULL,
			secret TEXT NOT NULL,
			FOREIGN KEY(user_id) REFERENCES users(id)
		);
	`)
	if err != nil {
		log.Fatalf("Failed to create tables: %v", err)
	}
}