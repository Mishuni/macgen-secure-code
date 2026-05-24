
package main

import (
	"crypto/rand"
	"crypto/sha256"
	"golang.org/x/crypto/pbkdf2"
	"encoding/hex"
	"fmt"
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