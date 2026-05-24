package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/google/uuid"
	"github.com/gofiber/fiber/v2"
	_ "github.com/mattn/go-sqlite3"
)

type Invitation struct {
	ID    string `json:"invite_id"`
	Email string `json:"email"`
}

type User struct {
	ID       string `json:"id"`
	Username string `json:"user_name"`
	Password string `json:"password"`
}

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createInvitationsTable := `
	CREATE TABLE IF NOT EXISTS invitations (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE
	);`
	if _, err := db.Exec(createInvitationsTable); err != nil {
		log.Fatal(err)
	}

	createUsersTable := `
	CREATE TABLE IF NOT EXISTS users (
		id TEXT PRIMARY KEY,
		username TEXT UNIQUE,
		password TEXT
	);`
	if _, err := db.Exec(createUsersTable); err != nil {
		log.Fatal(err)
	}
}

func inviteUser(c *fiber.Ctx) error {
	var invitation Invitation
	if err := c.BodyParser(&invitation); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request"})
	}

	if invitation.Email == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Email is required"})
	}

	var existingID string
	err := db.QueryRow("SELECT id FROM invitations WHERE email = ?", invitation.Email).Scan(&existingID)
	if err == nil {
		return c.JSON(fiber.Map{"invite_id": existingID, "message": "Invitation already exists"})
	}

	invitation.ID = uuid.NewString()
	_, err = db.Exec("INSERT INTO invitations (id, email) VALUES (?, ?)", invitation.ID, invitation.Email)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": "Failed to create invitation"})
	}

	return c.JSON(fiber.Map{"invite_id": invitation.ID, "message": "Invitation created successfully"})
}

func createUser(c *fiber.Ctx) error {
	var user User
	if err := c.BodyParser(&user); err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request"})
	}

	if user.Username == "" || user.Password == "" || user.ID == "" {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Username, password, and invite_id are required"})
	}

	var inviteID string
	err := db.QueryRow("SELECT id FROM invitations WHERE id = ?", user.ID).Scan(&inviteID)
	if err != nil {
		return c.Status(http.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid invite_id"})
	}

	_, err = db.Exec("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", uuid.NewString(), user.Username, user.Password)
	if err != nil {
		if err.Error() == "UNIQUE constraint failed: users.username" {
			return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "Username already exists. Try providing a different username."})
		}
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": "Failed to create user"})
	}

	return c.JSON(fiber.Map{"message": "User created successfully"})
}

func main() {
	initDB()
	defer db.Close()

	app := fiber.New()

	app.Post("/invite_user", inviteUser)
	app.Post("/create_user", createUser)

	log.Fatal(app.Listen(":5000"))
}