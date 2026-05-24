package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"regexp"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

type Invitation struct {
	InviteID string `json:"invite_id"`
	Email    string `json:"email"`
}

type CreateUserRequest struct {
	InviteID  string `json:"invite_id"`
	UserName  string `json:"user_name"`
	Password  string `json:"password"`
}

type ResponseMessage struct {
	Message string `json:"message"`
}

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS invitations (
		invite_id TEXT PRIMARY KEY,
		email TEXT UNIQUE NOT NULL
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}
}

func main() {
	app := fiber.New()

	app.Post("/invite_user", inviteUser)
	app.Post("/create_user", createUser)

	log.Fatal(app.Listen(":5000"))
}

func inviteUser(c *fiber.Ctx) error {
	var invitation Invitation
	if err := c.BodyParser(&invitation); err != nil {
		return c.Status(http.StatusBadRequest).JSON(ResponseMessage{Message: "Invalid request"})
	}

	if !isValidEmail(invitation.Email) {
		return c.Status(http.StatusBadRequest).JSON(ResponseMessage{Message: "Invalid email format"})
	}

	inviteID := uuid.New().String()
	_, err := db.Exec("INSERT OR IGNORE INTO invitations (invite_id, email) VALUES (?, ?)", inviteID, invitation.Email)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(ResponseMessage{Message: "Failed to create invitation"})
	}

	return c.JSON(Invitation{InviteID: inviteID, Email: invitation.Email})
}

func createUser(c *fiber.Ctx) error {
	var req CreateUserRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(ResponseMessage{Message: "Invalid request"})
	}

	if !isValidUserName(req.UserName) {
		return c.Status(http.StatusBadRequest).JSON(ResponseMessage{Message: "Invalid username"})
	}

	if len(req.Password) < 6 {
		return c.Status(http.StatusBadRequest).JSON(ResponseMessage{Message: "Password must be at least 6 characters"})
	}

	var email string
	err := db.QueryRow("SELECT email FROM invitations WHERE invite_id = ?", req.InviteID).Scan(&email)
	if err != nil {
		if err == sql.ErrNoRows {
			return c.Status(http.StatusUnauthorized).JSON(ResponseMessage{Message: "Invalid invite_id"})
		}
		return c.Status(http.StatusInternalServerError).JSON(ResponseMessage{Message: "Failed to validate invitation"})
	}

	// Here you would normally create the user in the database.
	// For this example, we will just return a success message.
	return c.JSON(ResponseMessage{Message: "User created successfully"})
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func isValidUserName(userName string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9_]{3,20}$`)
	return re.MatchString(userName)
}