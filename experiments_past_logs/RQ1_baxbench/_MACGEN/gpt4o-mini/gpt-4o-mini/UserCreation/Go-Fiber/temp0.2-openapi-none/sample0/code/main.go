package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"regexp"

	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Invitation struct {
	InviteID string `json:"invite_id"`
	Email    string `json:"email"`
}

type User struct {
	InviteID string `json:"invite_id"`
	Username string `json:"user_name"`
	Password string `json:"password"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTable := `
	CREATE TABLE IF NOT EXISTS invitations (
		invite_id TEXT PRIMARY KEY,
		email TEXT UNIQUE
	);
	CREATE TABLE IF NOT EXISTS users (
		username TEXT PRIMARY KEY,
		password TEXT
	);`
	_, err = db.Exec(createTable)
	if err != nil {
		log.Fatal(err)
	}
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func inviteUser(c *fiber.Ctx) error {
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

	var existingEmail string
	err := db.QueryRow("SELECT email FROM invitations WHERE invite_id = ?", user.InviteID).Scan(&existingEmail)
	if err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid invite_id"})
	}

	var existingUsername string
	err = db.QueryRow("SELECT username FROM users WHERE username = ?", user.Username).Scan(&existingUsername)
	if err == nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Username already exists. Try providing different username."})
	}

	_, err = db.Exec("INSERT INTO users (username, password) VALUES (?, ?)", user.Username, user.Password)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": "Failed to create user"})
	}

	return c.JSON(fiber.Map{"message": "User created"})
}

func main() {
	defer db.Close()

	app := fiber.New()

	app.Post("/invite_user", inviteUser)
	app.Post("/create_user", createUser)

	log.Fatal(app.Listen(":5000"))
}