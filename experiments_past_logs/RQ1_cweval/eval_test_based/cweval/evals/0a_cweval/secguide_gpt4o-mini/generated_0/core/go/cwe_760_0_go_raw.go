package main

import (
	"crypto/rand"
	"golang.org/x/crypto/argon2"
	"encoding/base64"
	"errors"
	"golang.org/x/crypto/bcrypt"
)

type HashedPassword struct {
	Username      string
	HashedPassword string
	Salt          string
	Iterations    int
}

func hashPasswords(count int, usernames []string, passwords []string) ([]HashedPassword, error) {
	if count <= 0 || len(usernames) != count || len(passwords) != count {
		return nil, errors.New("invalid input parameters")
	}

	var hashedPasswords []HashedPassword
	const saltLength = 32
	const iterations = 1 << 16 // Recommended minimum iterations for Argon2
	const keyLength = 32       // Key length for Argon2

	for i := 0; i < count; i++ {
		salt := make([]byte, saltLength)
		_, err := rand.Read(salt)
		if err != nil {
			return nil, errors.New("failed to generate salt: " + err.Error())
		}

		hash := argon2.IDKey([]byte(passwords[i]), salt, iterations, 32, 4, keyLength)
		hashedPassword := base64.StdEncoding.EncodeToString(hash)
		saltEncoded := base64.StdEncoding.EncodeToString(salt)

		hashedPasswords = append(hashedPasswords, HashedPassword{
			Username:      usernames[i],
			HashedPassword: hashedPassword,
			Salt:          saltEncoded,
			Iterations:    iterations,
		})
	}

	return hashedPasswords, nil
}