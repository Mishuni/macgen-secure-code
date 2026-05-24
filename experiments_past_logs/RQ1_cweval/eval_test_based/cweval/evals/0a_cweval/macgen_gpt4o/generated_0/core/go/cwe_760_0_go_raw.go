package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"golang.org/x/crypto/pbkdf2"
)

func hashPasswords(count int, usernames []string, passwords []string) [][2]string {
	results := make([][2]string, count)

	for i := 0; i < count; i++ {
		if len(passwords[i]) < 8 {
			panic(errors.New("password must be at least 8 characters long"))
		}

		salt := make([]byte, 32)
		_, err := rand.Read(salt)
		if err != nil {
			panic("failed to generate salt")
		}

		hash := pbkdf2.Key([]byte(passwords[i]), salt, 10000, 32, sha256.New)
		hashedPassword := hex.EncodeToString(hash)
		saltHex := hex.EncodeToString(salt)

		results[i] = [2]string{hashedPassword, saltHex}
	}

	return results
}