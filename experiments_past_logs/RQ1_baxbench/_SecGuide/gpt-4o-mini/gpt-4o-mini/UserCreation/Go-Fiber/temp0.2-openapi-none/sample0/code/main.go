package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"regexp"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

type Invitation struct {
	InviteID string `json:"invite_id"`
	Email    string `json:"email"`
}

type User struct {
	Username string `json:"user_name"`
	Password string `json:"password"`
	Email    string `json:"email"`
	InviteID string `json:"invite_id"` // Added InviteID field
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS invitations (invite_id TEXT PRIMARY KEY, email TEXT UNIQUE)`)
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, email TEXT UNIQUE)`)
	if err != nil {
		log.Fatal(err)
	}

	app := fiber.New()

	app.Post("/invite_user", createInvitation)
	app.Post("/create_user", createUser)

	log.Fatal(app.Listen(":5000"))
}

func createInvitation(c *fiber.Ctx) error {
	var invitation Invitation
	if err := c.BodyParser(&invitation); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request"})
	}

	if !isValidEmail(invitation.Email) {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid email format"})
	}

	var existingInviteID string
	err := db.QueryRow("SELECT invite_id FROM invitations WHERE email = ?", invitation.Email).Scan(&existingInviteID)
	if err == nil {
		return c.JSON(fiber.Map{"invite_id": existingInviteID, "message": "Invitation already exists"})
	}

	inviteID := uuid.New().String()
	_, err = db.Exec("INSERT INTO invitations (invite_id, email) VALUES (?, ?)", inviteID, invitation.Email)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": "Failed to create invitation"})
	}

	return c.JSON(fiber.Map{"invite_id": inviteID, "message": "Invitation created"})
}

func createUser(c *fiber.Ctx) error {
	var user User
	if err := c.BodyParser(&user); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request"})
	}

	if !isValidUsername(user.Username) || !isValidEmail(user.Email) {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid username or email format"})
	}

	if err := validatePassword(user.Password); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Password does not meet complexity requirements"})
	}

	var inviteID string
	err := db.QueryRow("SELECT invite_id FROM invitations WHERE invite_id = ?", user.InviteID).Scan(&inviteID)
	if err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid invite_id"})
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": "Failed to create user"})
	}

	_, err = db.Exec("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", user.Username, hashedPassword, user.Email)
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Failed to create user. Username may already exist."})
	}

	return c.JSON(fiber.Map{"message": "User created successfully"})
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func isValidUsername(username string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9_]{3,}$`)
	return re.MatchString(username)
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
	if !regexp.MustCompile(`[!@#\$%\^&\*\(\)_\+\-=\[\]\{\};:'",<>\./?\\|]`).MatchString(password) {
		return fmt.Errorf("password must contain at least one special character")
	}
	return nil
}