package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

func main() {
	app := fiber.New()

	// Initialize the database
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	app.Post("/invite_user", func(c *fiber.Ctx) error {
		type Request struct {
			Email string `json:"email"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request"})
		}

		// Check if the email already has an invitation
		var inviteID string
		err := db.QueryRow("SELECT invite_id FROM invitations WHERE email = ?", req.Email).Scan(&inviteID)
		if err == sql.ErrNoRows {
			// Create a new invitation
			inviteID = uuid.New().String()
			_, err := db.Exec("INSERT INTO invitations (invite_id, email) VALUES (?, ?)", inviteID, req.Email)
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Failed to create invitation"})
			}
		} else if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Database error"})
		}

		return c.JSON(fiber.Map{"invite_id": inviteID, "message": "Invitation created"})
	})

	app.Post("/create_user", func(c *fiber.Ctx) error {
		type Request struct {
			InviteID string `json:"invite_id"`
			UserName string `json:"user_name"`
			Password string `json:"password"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request"})
		}

		// Validate invitation
		var email string
		err := db.QueryRow("SELECT email FROM invitations WHERE invite_id = ?", req.InviteID).Scan(&email)
		if err == sql.ErrNoRows {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid invite_id"})
		} else if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Database error"})
		}

		// Check if username already exists
		var existingUser string
		err = db.QueryRow("SELECT user_name FROM users WHERE user_name = ?", req.UserName).Scan(&existingUser)
		if err != sql.ErrNoRows {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Username already exists. Try providing different username."})
		}

		// Create user
		_, err = db.Exec("INSERT INTO users (user_name, password, email) VALUES (?, ?, ?)", req.UserName, req.Password, email)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Failed to create user"})
		}

		return c.JSON(fiber.Map{"message": "User created"})
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	createInvitationsTable := `
	CREATE TABLE IF NOT EXISTS invitations (
		invite_id TEXT PRIMARY KEY,
		email TEXT UNIQUE NOT NULL
	);`

	createUsersTable := `
	CREATE TABLE IF NOT EXISTS users (
		user_name TEXT PRIMARY KEY,
		password TEXT NOT NULL,
		email TEXT NOT NULL
	);`

	if _, err := db.Exec(createInvitationsTable); err != nil {
		log.Fatalf("Failed to create invitations table: %v", err)
	}

	if _, err := db.Exec(createUsersTable); err != nil {
		log.Fatalf("Failed to create users table: %v", err)
	}
}