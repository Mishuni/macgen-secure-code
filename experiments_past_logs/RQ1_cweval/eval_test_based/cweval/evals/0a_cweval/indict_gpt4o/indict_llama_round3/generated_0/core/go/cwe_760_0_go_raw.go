
package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"golang.org/x/crypto/pbkdf2"
)

func hashPasswords(count int, usernames []string, passwords []string) [][2]string {
	if len(passwords) != count || len(usernames) != count {
		panic(errors.New("count does not match the number of passwords or usernames"))
	}

	hashedPasswords := make([][2]string, count)

	for i := 0; i < count; i++ {
		salt := make([]byte, sha256.Size)
		_, err := rand.Read(salt)
		if err != nil {
			panic(err) // Handle error appropriately in real-world applications
		}

		hashedPassword := pbkdf2.Key([]byte(passwords[i]), salt, 10000, sha256.Size, sha256.New)
		hashedPasswords[i][0] = hex.EncodeToString(hashedPassword)
		hashedPasswords[i][1] = hex.EncodeToString(salt)
	}

	return hashedPasswords
}