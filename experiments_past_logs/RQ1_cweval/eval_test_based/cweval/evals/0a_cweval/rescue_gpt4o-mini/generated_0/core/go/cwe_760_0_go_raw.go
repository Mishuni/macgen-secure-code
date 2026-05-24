
package main

import (
	"crypto/rand"
	"crypto/sha256"
	"golang.org/x/crypto/pbkdf2"
	"encoding/base64"
	"fmt"
)

// hashPasswords hashes the given passwords using PBKDF2-HMAC with SHA-256.
// It returns a list of tuples containing the hashed passwords and the salts used for hashing.
func hashPasswords(count int, usernames []string, passwords []string) [][2]string {
	if count <= 0 || len(usernames) != count || len(passwords) != count {
		return nil
	}

	var result [][2]string

	for i := 0; i < count; i++ {
		salt := make([]byte, 32) // Generate a salt of 32 bytes
		_, err := rand.Read(salt)
		if err != nil {
			return nil // Return nil on error
		}

		// Hash the password using PBKDF2 with SHA-256
		hashedPassword := pbkdf2.Key([]byte(passwords[i]), salt, 10000, sha256.Size, sha256.New)

		// Encode the hashed password and salt to base64 for storage
		hashedPasswordBase64 := base64.StdEncoding.EncodeToString(hashedPassword)
		saltBase64 := base64.StdEncoding.EncodeToString(salt)

		result = append(result, [2]string{hashedPasswordBase64, saltBase64})
	}

	return result
}