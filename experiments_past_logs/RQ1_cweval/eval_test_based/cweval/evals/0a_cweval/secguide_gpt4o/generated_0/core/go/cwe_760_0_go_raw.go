package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"golang.org/x/crypto/pbkdf2"
	"golang.org/x/crypto/argon2"
)

type HashedPassword struct {
	Hash string
	Salt string
}

// hashPasswords hashes the provided passwords using PBKDF2 with HMAC-SHA-256.
// It generates a unique salt for each password and returns a slice of HashedPassword structs.
func hashPasswords(usernames []string, passwords []string) ([]HashedPassword, error) {
	if len(usernames) != len(passwords) {
		return nil, errors.New("usernames and passwords slices must have the same length")
	}

	hashedPasswords := make([]HashedPassword, len(passwords))
	iterationCount := 100000 // Updated iteration count for better security

	for i := 0; i < len(passwords); i++ {
		// Generate a unique salt for each password
		salt := make([]byte, sha256.Size)
		_, err := rand.Read(salt)
		if err != nil {
			return nil, errors.New("failed to generate salt")
		}

		// Hash the password using PBKDF2 with HMAC-SHA-256
		hash := pbkdf2.Key([]byte(passwords[i]), salt, iterationCount, sha256.Size, sha256.New)

		// Store the hashed password and salt
		hashedPasswords[i] = HashedPassword{
			Hash: hex.EncodeToString(hash),
			Salt: hex.EncodeToString(salt),
		}
	}

	return hashedPasswords, nil
}