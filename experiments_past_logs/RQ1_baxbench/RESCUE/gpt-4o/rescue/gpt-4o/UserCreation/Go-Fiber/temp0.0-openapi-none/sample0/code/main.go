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

	// Create necessary tables
	createTables(db)

	// Route to create an invitation
	app.Post("/invite_user", func(c *fiber.Ctx) error {
		type Request struct {
			Email string `json:"email"`
		}
		type Response struct {
			InviteID string `json:"invite_id"`
			Message  string `json:"message"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request body"})
		}

		if req.Email == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Email is required"})
		}

		// Check if the email already has an invitation
		var existingInviteID string
		err := db.QueryRow("SELECT invite_id FROM invitations WHERE email = ?", req.Email).Scan(&existingInviteID)
		if err == nil {
			return c.JSON(Response{InviteID: existingInviteID, Message: "Invitation already exists"})
		}

		// Create a new invitation
		inviteID := uuid.New().String()
		_, err = db.Exec("INSERT INTO invitations (invite_id, email) VALUES (?, ?)", inviteID, req.Email)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Failed to create invitation"})
		}

		return c.JSON(Response{InviteID: inviteID, Message: "Invitation created successfully"})
	})

	// Route to create a user
	app.Post("/create_user", func(c *fiber.Ctx) error {
		type Request struct {
			InviteID string `json:"invite_id"`
			UserName string `json:"user_name"`
			Password string `json:"password"`
		}
		type Response struct {
			Message string `json:"message"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request body"})
		}

		if req.InviteID == "" || req.UserName == "" || req.Password == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "All fields are required"})
		}

		// Validate the invitation
		var email string
		err := db.QueryRow("SELECT email FROM invitations WHERE invite_id = ?", req.InviteID).Scan(&email)
		if err != nil {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid invite_id"})
		}

		// Check if the username already exists
		var existingUser string
		err = db.QueryRow("SELECT user_name FROM users WHERE user_name = ?", req.UserName).Scan(&existingUser)
		if err == nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Username already exists. Try providing different username."})
		}

		// Create the user
		_, err = db.Exec("INSERT INTO users (user_name, password, email) VALUES (?, ?, ?)", req.UserName, req.Password, email)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Failed to create user"})
		}

		// Delete the invitation after use
		_, err = db.Exec("DELETE FROM invitations WHERE invite_id = ?", req.InviteID)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Failed to clean up invitation"})
		}

		return c.JSON(Response{Message: "User created successfully"})
	})

	// Start the server
	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	// Create invitations table
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS invitations (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			invite_id TEXT NOT NULL UNIQUE,
			email TEXT NOT NULL UNIQUE
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create invitations table: %v", err)
	}

	// Create users table
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_name TEXT NOT NULL UNIQUE,
			password TEXT NOT NULL,
			email TEXT NOT NULL
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create users table: %v", err)
	}
}