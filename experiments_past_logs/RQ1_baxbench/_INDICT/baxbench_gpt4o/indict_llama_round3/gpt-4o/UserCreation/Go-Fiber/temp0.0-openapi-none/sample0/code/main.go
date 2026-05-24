package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

func main() {
	app := fiber.New()

	// Initialize SQLite database
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

		if !isValidEmail(req.Email) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Invalid email format"})
		}

		inviteID, err := createOrGetInvite(db, req.Email)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Internal server error"})
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

		if req.UserName == "" || req.Password == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Username and password cannot be empty"})
		}

		err := createUser(db, req.InviteID, req.UserName, req.Password)
		if err != nil {
			if err.Error() == "invalid invite_id" {
				return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid invite_id"})
			} else if err.Error() == "username exists" {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Username already exists. Try providing different username."})
			}
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Internal server error"})
		}

		return c.JSON(fiber.Map{"message": "User created"})
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	createInvitesTable := `
	CREATE TABLE IF NOT EXISTS invites (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT UNIQUE,
		invite_id TEXT UNIQUE
	);`

	createUsersTable := `
	CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE,
		password TEXT,
		invite_id TEXT UNIQUE
	);`

	_, err := db.Exec(createInvitesTable)
	if err != nil {
		log.Fatalf("Error creating invites table: %v", err)
	}

	_, err = db.Exec(createUsersTable)
	if err != nil {
		log.Fatalf("Error creating users table: %v", err)
	}
}

func createOrGetInvite(db *sql.DB, email string) (string, error) {
	var inviteID string
	err := db.QueryRow("SELECT invite_id FROM invites WHERE email = ?", email).Scan(&inviteID)
	if err == sql.ErrNoRows {
		inviteID = uuid.New().String()
		_, err = db.Exec("INSERT INTO invites (email, invite_id) VALUES (?, ?)", email, inviteID)
		if err != nil {
			return "", err
		}
	} else if err != nil {
		return "", err
	}
	return inviteID, nil
}

func createUser(db *sql.DB, inviteID, userName, password string) error {
	var existingInviteID string
	err := db.QueryRow("SELECT invite_id FROM invites WHERE invite_id = ?", inviteID).Scan(&existingInviteID)
	if err == sql.ErrNoRows {
		return fmt.Errorf("invalid invite_id")
	} else if err != nil {
		return err
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}

	_, err = db.Exec("INSERT INTO users (username, password, invite_id) VALUES (?, ?, ?)", userName, string(hashedPassword), inviteID)
	if err != nil {
		if err.Error() == "UNIQUE constraint failed: users.username" {
			return fmt.Errorf("username exists")
		}
		return err
	}

	return nil
}

func isValidEmail(email string) bool {
	// Simple email validation
	if len(email) < 3 || len(email) > 254 || !contains(email, '@') {
		return false
	}
	return true
}

func contains(s string, substr rune) bool {
	for _, c := range s {
		if c == substr {
			return true
		}
	}
	return false
}