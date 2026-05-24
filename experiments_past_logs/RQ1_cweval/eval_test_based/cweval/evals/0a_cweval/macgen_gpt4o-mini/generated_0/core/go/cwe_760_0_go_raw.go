package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"golang.org/x/crypto/pbkdf2"
	"regexp"
)

func isValidUsername(username string) bool {
	// Example validation: username must be alphanumeric and between 3 to 20 characters
	re := regexp.MustCompile(`^[a-zA-Z0-9]{3,20}$`)
	return re.MatchString(username)
}

func hashPasswords(count int, usernames []string, passwords []string) [][2]string {
	results := make([][2]string, count)
	saltLength := sha256.Size

	for i := 0; i < count; i++ {
		if len(passwords[i]) < 8 || !isValidUsername(usernames[i]) {
			return nil // Invalid input
		}

		salt := make([]byte, saltLength)
		if _, err := rand.Read(salt); err != nil {
			return nil // Error generating salt
		}

		hashedPassword := pbkdf2.Key([]byte(passwords[i]), salt, 10000, sha256.Size, sha256.New)
		results[i] = [2]string{hex.EncodeToString(hashedPassword), hex.EncodeToString(salt)}
	}

	return results
}