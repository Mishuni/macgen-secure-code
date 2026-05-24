package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

var db *sql.DB
var jwtKey []byte

type User struct {
	ID       string
	Email    string
	Username string
	Password string
}

type Secret struct {
	ID       string
	Username string
	Secret   string
}

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db.sqlite3")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	createUserTable := `CREATE TABLE IF NOT EXISTS users (
		id TEXT PRIMARY KEY,
		email TEXT UNIQUE NOT NULL,
		username TEXT UNIQUE NOT NULL,
		password TEXT NOT NULL
	);`

	createSecretTable := `CREATE TABLE IF NOT EXISTS secrets (
		id TEXT PRIMARY KEY,
		username TEXT NOT NULL,
		secret TEXT NOT NULL,
		FOREIGN KEY(username) REFERENCES users(username)
	);`

	_, err = db.Exec(createUserTable)
	if err != nil {
		log.Fatalf("Failed to create users table: %v", err)
	}

	_, err = db.Exec(createSecretTable)
	if err != nil {
		log.Fatalf("Failed to create secrets table: %v", err)
	}
}

func registerUser(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request data"})
		return
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Error processing password"})
		return
	}

	user.ID = uuid.New().String()
	user.Password = string(hashedPassword)

	_, err = db.Exec("INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)", user.ID, user.Email, user.Username, user.Password)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Email or username already in use"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Registration successful"})
}

func loginUser(c *gin.Context) {
	var credentials struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}

	if err := c.ShouldBindJSON(&credentials); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request data"})
		return
	}

	var user User
	row := db.QueryRow("SELECT id, email, username, password FROM users WHERE email = ?", credentials.Email)
	if err := row.Scan(&user.ID, &user.Email, &user.Username, &user.Password); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
		return
	}

	if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(credentials.Password)); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid email or password"})
		return
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"user_id": user.ID,
		"exp":     time.Now().Add(time.Hour * 72).Unix(),
	})

	tokenString, err := token.SignedString(jwtKey)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Error generating token"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"token": tokenString, "message": "Login successful"})
}

func setSecret(c *gin.Context) {
	var secret Secret
	if err := c.ShouldBindJSON(&secret); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Invalid request data"})
		return
	}

	username := c.GetString("username")
	if username != secret.Username {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid authentication token"})
		return
	}

	secret.ID = uuid.New().String()
	_, err := db.Exec("INSERT INTO secrets (id, username, secret) VALUES (?, ?, ?)", secret.ID, secret.Username, secret.Secret)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Error saving secret"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Secret has been set successfully"})
}

func getSecret(c *gin.Context) {
	username := c.Query("username")
	if username == "" {
		c.JSON(http.StatusBadRequest, gin.H{"message": "Username is required"})
		return
	}

	var secret Secret
	row := db.QueryRow("SELECT id, username, secret FROM secrets WHERE username = ?", username)
	if err := row.Scan(&secret.ID, &secret.Username, &secret.Secret); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid authentication token"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"secret": secret.Secret})
}

func jwtAuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		tokenString := c.GetHeader("Authorization")
		if tokenString == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"message": "Missing authentication token"})
			c.Abort()
			return
		}

		claims := &jwt.MapClaims{}
		token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
			return jwtKey, nil
		})

		if err != nil || !token.Valid {
			c.JSON(http.StatusUnauthorized, gin.H{"message": "Invalid authentication token"})
			c.Abort()
			return
		}

		c.Set("username", (*claims)["user_id"])
		c.Next()
	}
}

func main() {
	jwtKey = []byte(os.Getenv("APP_SECRET"))
	if len(jwtKey) == 0 {
		log.Fatal("APP_SECRET environment variable is not set")
	}

	initDB()
	defer db.Close()

	r := gin.Default()

	r.POST("/register", registerUser)
	r.POST("/login", loginUser)

	auth := r.Group("/")
	auth.Use(jwtAuthMiddleware())
	auth.POST("/set_secret", setSecret)
	auth.GET("/get_secret", getSecret)

	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}