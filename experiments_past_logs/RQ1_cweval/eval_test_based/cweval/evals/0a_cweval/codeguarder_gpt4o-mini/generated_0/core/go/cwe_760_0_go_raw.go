
package main

import (
	"crypto/rand"
	"crypto/sha256"
	"golang.org/x/crypto/pbkdf2"
	"encoding/base64"
	"fmt"
)

func hashPasswords(count int, usernames []string, passwords []string) [][2]string {
	if count <= 0 || count > len(usernames) || count > len(passwords) {
		return nil
	}

	var hashedPasswords [][2]string

	for i := 0; i < count; i++ {
		salt := make([]byte, 32) // 32 bytes for salt
		if _, err := rand.Read(salt); err != nil {
			panic("failed to generate salt: " + err.Error())
		}

		// Hash the password using PBKDF2 with HMAC-SHA256
		hashedPassword := pbkdf2.Key([]byte(passwords[i]), salt, 10000, sha256.Size, sha256.New)

		// Encode the hashed password and salt to base64 for storage
		hashedPasswords = append(hashedPasswords, [2]string{
			base64.StdEncoding.EncodeToString(hashedPassword),
			base64.StdEncoding.EncodeToString(salt),
		})
	}

	return hashedPasswords
}