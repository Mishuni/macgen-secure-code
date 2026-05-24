package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"regexp"

	"golang.org/x/crypto/pbkdf2"
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
