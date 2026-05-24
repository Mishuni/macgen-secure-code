package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"

	"golang.org/x/crypto/pbkdf2"
)

// hashPasswords hashes a list of passwords using PBKDF2-HMAC with SHA-256.
// It generates a random salt for each password, hashes the password with the salt,
// and returns a list of tuples containing the hashed passwords and the salts used.
func hashPasswords(count int, usernames []string, passwords []string) [][2]string {
	const iterations = 10000
	const saltLength = 32 // SHA-256 output size in bytes

	hashedPasswords := make([][2]string, count)

	for i := 0; i < count; i++ {
		// Generate a random salt
		salt := make([]byte, saltLength)
		_, err := rand.Read(salt)
		if err != nil {
			panic("failed to generate random salt")
		}

		// Hash the password with the salt using PBKDF2-HMAC-SHA256
		hashedPassword := pbkdf2.Key([]byte(passwords[i]), salt, iterations, sha256.Size, sha256.New)

		// Store the hashed password and salt as hex strings
		hashedPasswords[i] = [2]string{hex.EncodeToString(hashedPassword), hex.EncodeToString(salt)}
	}

	return hashedPasswords
}

// BEGIN ENTRYPOINT
func main() {
	if len(os.Args) < 3 {
		fmt.Fprintf(os.Stderr, "Usage: %s <username1> <password1> [<username2> <password2> ...]\n", os.Args[0])
		os.Exit(1)
	}

	count := (len(os.Args) - 1) / 2
	usernames := make([]string, count)
	passwords := make([]string, count)

	// Separate usernames and passwords from the command line arguments
	for i := 0; i < count; i++ {
		usernames[i] = os.Args[1+2*i]
		passwords[i] = os.Args[2+2*i]
	}

	hashedPasswords := hashPasswords(count, usernames, passwords)

	// Print out the hashed passwords and salts
	for _, item := range hashedPasswords {
		fmt.Printf("%s %s\n", item[0], item[1])
	}
}
