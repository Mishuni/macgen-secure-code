package main

import (
	"crypto/rand"
	"encoding/base64"
	"errors"
	"fmt"
	"os"

	"golang.org/x/crypto/argon2"
)

type HashedPassword struct {
	Username       string
	HashedPassword string
	Salt           string
	Iterations     int
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
			Username:       usernames[i],
			HashedPassword: hashedPassword,
			Salt:           saltEncoded,
			Iterations:     iterations,
		})
	}

	return hashedPasswords, nil
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
