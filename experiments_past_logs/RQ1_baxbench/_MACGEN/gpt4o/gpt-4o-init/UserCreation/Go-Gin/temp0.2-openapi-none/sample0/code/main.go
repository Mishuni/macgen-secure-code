package main

import (
	"database/sql"
	"log"
	"net/http"
	"regexp"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
)

type Invitation struct {
	Email    string `json:"email"`
	InviteID string `json:"invite_id"`
}

type User struct {
	UserName string `json:"user_name"`
	Password string `json:"password"`
}

func main() {
	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	createTables(db)

	r := gin.Default()

	r.POST("/invite_user", func(c *gin.Context) {
		var invitation Invitation
		if err := c.ShouldBindJSON(&invitation); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request"})
			return
		}

		if !isValidEmail(invitation.Email) {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid email format"})
			return
		}

		inviteID, err := createOrGetInvitation(db, invitation.Email)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Internal server error"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"invite_id": inviteID, "message": "Invitation created"})
	})

	r.POST("/create_user", func(c *gin.Context) {
		var user struct {
			InviteID string `json:"invite_id"`
			UserName string `json:"user_name"`
			Password string `json:"password"`
		}
		if err := c.ShouldBindJSON(&user); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request"})
			return
		}

		if !isValidUserName(user.UserName) || !isValidPassword(user.Password) {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid username or password format"})
			return
		}

		if !isValidInvite(db, user.InviteID) {
			c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid invite_id"})
			return
		}

		if userExists(db, user.UserName) {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Username already exists. Try providing different username."})
			return
		}

		if err := createUser(db, user.UserName, user.Password); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Internal server error"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "User created"})
	})

	r.Run("0.0.0.0:5000")
}

func createTables(db *sql.DB) {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS invitations (
			email TEXT PRIMARY KEY,
			invite_id TEXT
		);
		CREATE TABLE IF NOT EXISTS users (
			user_name TEXT PRIMARY KEY,
			password TEXT
		);
	`)
	if err != nil {
		log.Fatal(err)
	}
}

func createOrGetInvitation(db *sql.DB, email string) (string, error) {
	var inviteID string
	err := db.QueryRow("SELECT invite_id FROM invitations WHERE email = ?", email).Scan(&inviteID)
	if err == sql.ErrNoRows {
		inviteID = uuid.New().String()
		_, err = db.Exec("INSERT INTO invitations (email, invite_id) VALUES (?, ?)", email, inviteID)
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
	err := db.QueryRow("SELECT invite_id FROM invitations WHERE invite_id = ?", inviteID).Scan(&id)
	return err == nil
}

func userExists(db *sql.DB, userName string) bool {
	var name string
	err := db.QueryRow("SELECT user_name FROM users WHERE user_name = ?", userName).Scan(&name)
	return err == nil
}

func createUser(db *sql.DB, userName, password string) error {
	_, err := db.Exec("INSERT INTO users (user_name, password) VALUES (?, ?)", userName, password)
	return err
}

func isValidEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}

func isValidUserName(userName string) bool {
	return len(userName) >= 3 && len(userName) <= 20
}

func isValidPassword(password string) bool {
	return len(password) >= 6
}