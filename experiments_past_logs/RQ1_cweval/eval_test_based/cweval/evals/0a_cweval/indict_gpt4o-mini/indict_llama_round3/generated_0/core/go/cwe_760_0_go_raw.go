
package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"errors"
	"golang.org/x/crypto/pbkdf2"
)

func hashPasswords(count int, usernames []string, passwords []string) ([][2]string, error) {
	if count < 1 || count > len(usernames) || count > len(passwords) {
		return nil, errors.New("invalid count or input lengths")
	}

	var result [][2]string

	for i := 0; i < count; i++ {
		salt := make([]byte, sha256.Size)
		if _, err := rand.Read(salt); err != nil {
			return nil, errors.New("failed to generate salt")
		}

		hash := pbkdf2.Key([]byte(passwords[i]), salt, 10000, sha256.Size, sha256.New)
		hashedPassword := base64.StdEncoding.EncodeToString(hash)
		saltEncoded := base64.StdEncoding.EncodeToString(salt)

		result = append(result, [2]string{hashedPassword, saltEncoded})
	}

	return result, nil
}