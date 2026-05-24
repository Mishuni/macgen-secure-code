package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"regexp"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	app := fiber.New()

	db, err := sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	createTables(db)

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
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
		}

		if !isValidEmail(req.Email) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid email format"})
		}

		var inviteID string
		err := db.QueryRow("SELECT invite_id FROM invitations WHERE email = ?", req.Email).Scan(&inviteID)
		if err == sql.ErrNoRows {
			inviteID = uuid.New().String()
			_, err = db.Exec("INSERT INTO invitations (invite_id, email) VALUES (?, ?)", inviteID, req.Email)
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create invitation"})
			}
		} else if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Database error"})
		}

		return c.JSON(Response{InviteID: inviteID, Message: "Invitation created"})
	})

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
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
		}

		var email string
		err := db.QueryRow("SELECT email FROM invitations WHERE invite_id = ?", req.InviteID).Scan(&email)
		if err == sql.ErrNoRows {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid invite_id"})
		} else if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Database error"})
		}

		var existingUser string
		err = db.QueryRow("SELECT user_name FROM users WHERE user_name = ?", req.UserName).Scan(&existingUser)
		if err == nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Username already exists. Try providing different username."})
		} else if err != sql.ErrNoRows {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Database error"})
		}

		_, err = db.Exec("INSERT INTO users (user_name, password) VALUES (?, ?)", req.UserName, req.Password)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create user"})
		}

		return c.JSON(Response{Message: "User created"})
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTables(db *sql.DB) {
	createInvitationsTable := `
	CREATE TABLE IF NOT EXISTS invitations (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		invite_id TEXT NOT NULL UNIQUE,
		email TEXT NOT NULL UNIQUE
	);`
	_, err := db.Exec(createInvitationsTable)
	if err != nil {
		log.Fatalf("Failed to create invitations table: %v", err)
	}

	createUsersTable := `
	CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		user_name TEXT NOT NULL UNIQUE,
		password TEXT NOT NULL
	);`
	_, err = db.Exec(createUsersTable)
	if err != nil {
		log.Fatalf("Failed to create users table: %v", err)
	}
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}