package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

var jwtSecret []byte

func init() {
	jwtSecret = []byte(os.Getenv("APP_SECRET"))
	if len(jwtSecret) == 0 {
		log.Fatal("APP_SECRET environment variable is not set")
	}
}

func main() {
	app := fiber.New()

	db, err := sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	createTable(db)

	app.Post("/register", func(c *fiber.Ctx) error {
		type Request struct {
			Email    string `json:"email"`
			Password string `json:"password"`
			Name     string `json:"name"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request"})
		}

		if req.Email == "" || req.Password == "" || req.Name == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Invalid data"})
		}

		hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Internal server error"})
		}

		_, err = db.Exec("INSERT INTO users (id, email, password, name) VALUES (?, ?, ?, ?)", uuid.New().String(), req.Email, string(hashedPassword), req.Name)
		if err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Email already in use"})
		}

		return c.Status(fiber.StatusCreated).JSON(fiber.Map{"message": "Registration successful"})
	})

	app.Post("/login", func(c *fiber.Ctx) error {
		type Request struct {
			Email    string `json:"email"`
			Password string `json:"password"`
		}

		var req Request
		if err := c.BodyParser(&req); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Invalid request"})
		}

		if req.Email == "" || req.Password == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"message": "Invalid email or password"})
		}

		var id, hashedPassword string
		err := db.QueryRow("SELECT id, password FROM users WHERE email = ?", req.Email).Scan(&id, &hashedPassword)
		if err != nil {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid email or password"})
		}

		if err := bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(req.Password)); err != nil {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"message": "Invalid email or password"})
		}

		token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
			"user_id": id,
			"exp":     time.Now().Add(time.Hour * 72).Unix(),
		})

		tokenString, err := token.SignedString(jwtSecret)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"message": "Internal server error"})
		}

		return c.JSON(fiber.Map{"token": tokenString, "message": "Login successful"})
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func createTable(db *sql.DB) {
	createUserTableSQL := `CREATE TABLE IF NOT EXISTS users (
		"id" TEXT NOT NULL PRIMARY KEY,
		"email" TEXT UNIQUE,
		"password" TEXT,
		"name" TEXT
	);`

	statement, err := db.Prepare(createUserTableSQL)
	if err != nil {
		log.Fatal(err)
	}
	statement.Exec()
}