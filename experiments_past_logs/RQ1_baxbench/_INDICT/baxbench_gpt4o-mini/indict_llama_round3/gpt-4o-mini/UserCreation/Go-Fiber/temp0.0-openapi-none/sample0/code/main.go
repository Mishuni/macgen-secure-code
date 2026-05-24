package main

import (
	"database/sql"
	"log"
	"net/http"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

type Invitation struct {
	Email    string `json:"email"`
	InviteID string `json:"invite_id"`
}

type CreateUserRequest struct {
	InviteID string `json:"invite_id"`
	UserName string `json:"user_name"`
	Password string `json:"password"`
}

type ResponseMessage struct {
	Message string `json:"message"`
}

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("sqlite3", "db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	createTableSQL := `CREATE TABLE IF NOT EXISTS invitations (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE
	);`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatal(err)
	}

	createUsersTableSQL := `CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE,
		password TEXT
	);`
	_, err = db.Exec(createUsersTableSQL)
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

	var inviteID string
	err := db.QueryRow("SELECT id FROM invitations WHERE email = ?", invitation.Email).Scan(&inviteID)
	if err == sql.ErrNoRows {
		inviteID = uuid.NewString()
		_, err = db.Exec("INSERT INTO invitations (id, email) VALUES (?, ?)", inviteID, invitation.Email)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(ResponseMessage{Message: "Failed to create invitation"})
		}
	} else if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(ResponseMessage{Message: "Database error"})
	}

	return c.JSON(fiber.Map{
		"invite_id": inviteID,
		"message":   "Invitation email prepared",
	})
}

func createUser(c *fiber.Ctx) error {
	var req CreateUserRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(http.StatusBadRequest).JSON(ResponseMessage{Message: "Invalid request"})
	}

	var email string
	err := db.QueryRow("SELECT email FROM invitations WHERE id = ?", req.InviteID).Scan(&email)
	if err == sql.ErrNoRows {
		return c.Status(http.StatusUnauthorized).JSON(ResponseMessage{Message: "Invalid invite_id"})
	} else if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(ResponseMessage{Message: "Database error"})
	}

	_, err = db.Exec("INSERT INTO users (username, password) VALUES (?, ?)", req.UserName, req.Password)
	if err != nil {
		if sqliteErr, ok := err.(sqlite3.Error); ok && sqliteErr.ExtendedCode == sqlite3.ErrConstraintUnique {
			return c.Status(http.StatusBadRequest).JSON(ResponseMessage{Message: "Username already exists. Try providing different username."})
		}
		return c.Status(http.StatusInternalServerError).JSON(ResponseMessage{Message: "Failed to create user"})
	}

	return c.JSON(ResponseMessage{Message: "User created"})
}