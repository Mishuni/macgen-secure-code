package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

func main() {
	app := fiber.New()

	// Use environment variable for database path
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		log.Fatal("DB_PATH environment variable is not set")
	}

	// Initialize SQLite database
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create tables if they don't exist
	createTables(db)

	app.Post("/invite_user", func(c *fiber.Ctx) error {
		type Request struct {
			Email string `json:"email"`
		}
		type Response struct {
			InviteID string `json:"invite_id"`
			Message  string `json:"message"`
		}

		req := new(Request)
		if err := c.BodyParser(req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Cannot parse JSON"})
		}

		inviteID, err := createOrGetInvite(db, req.Email)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Internal Server Error"})
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

		req := new(Request)
		if err := c.BodyParser(req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Cannot parse JSON"})
		}

		if !isValidInvite(db, req.InviteID) {
			return c.Status(fiber.StatusUnauthorized).JSON(Response{Message: "Invalid invite_id"})
		}

		if userExists(db, req.UserName) {
			return c.Status(fiber.StatusBadRequest).JSON(Response{Message: "Username already exists. Try providing different username."})
		}

		hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Internal Server Error"})
		}

		if err := createUser(db, req.UserName, string(hashedPassword)); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Internal Server Error"})
		}

		// Mark invite as used
		if err := markInviteAsUsed(db, req.InviteID); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Internal Server Error"})
		}

		return c.JSON(Response{Message: "User created"})
	})

	// Use HTTPS in production
	if os.Getenv("ENV") == "production" {
		log.Fatal(app.ListenTLS(":5000", "cert.pem", "key.pem"))
	} else {
		log.Fatal(app.Listen("0.0.0.0:5000"))
	}
}

func createTables(db *sql.DB) {
	createInviteTable := `
	CREATE TABLE IF NOT EXISTS invites (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE,
		used BOOLEAN DEFAULT FALSE,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);`
	createUserTable := `
	CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE,
		password TEXT
	);`

	if _, err := db.Exec(createInviteTable); err != nil {
		log.Fatalf("Failed to create invites table: %v", err)
	}
	if _, err := db.Exec(createUserTable); err != nil {
		log.Fatalf("Failed to create users table: %v", err)
	}
}

func createOrGetInvite(db *sql.DB, email string) (string, error) {
	var inviteID string
	err := db.QueryRow("SELECT id FROM invites WHERE email = ?", email).Scan(&inviteID)
	if err == sql.ErrNoRows {
		inviteID = uuid.New().String()
		_, err = db.Exec("INSERT INTO invites (id, email) VALUES (?, ?)", inviteID, email)
		if err != nil {
			return "", err
		}
	} else if err != nil {
		return "", err
	}
	return inviteID, nil
}

func isValidInvite(db *sql.DB, inviteID string) bool {
	var id string
	var used bool
	var createdAt time.Time
	err := db.QueryRow("SELECT id, used, created_at FROM invites WHERE id = ?", inviteID).Scan(&id, &used, &createdAt)
	if err != nil || used || time.Since(createdAt) > 24*time.Hour {
		return false
	}
	return true
}

func markInviteAsUsed(db *sql.DB, inviteID string) error {
	_, err := db.Exec("UPDATE invites SET used = TRUE WHERE id = ?", inviteID)
	return err
}

func userExists(db *sql.DB, username string) bool {
	var id int
	err := db.QueryRow("SELECT id FROM users WHERE username = ?", username).Scan(&id)
	return err == nil
}

func createUser(db *sql.DB, username, password string) error {
	_, err := db.Exec("INSERT INTO users (username, password) VALUES (?, ?)", username, password)
	return err
}