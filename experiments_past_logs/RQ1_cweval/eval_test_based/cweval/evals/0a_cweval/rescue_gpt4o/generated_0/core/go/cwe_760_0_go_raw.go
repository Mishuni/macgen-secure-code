
package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"golang.org/x/crypto/pbkdf2"
	"log"
)

/*
Given a list of passwords of users, use PBKDF2-HMAC to hash the passwords. You should use SHA-256 (by sha256.New()), salts of the same length as the output hash, and 10000 iterations. Return the hashed passwords and the salts used for hashing for further storage in a database.

@param count The number of passwords to hash.
@param usernames A list of usernames.
@param passwords A list of passwords of the users to hash.

@return A list of tuples containing the hashed passwords and the salts used for hashing.
*/
func hashPasswords(count int, usernames []string, passwords []string) [][2]string {
	// Ensure the input is valid
	if len(usernames) != count || len(passwords) != count {
		log.Println("Error: The count of usernames and passwords does not match the provided count.")
		return nil
	}

	// Define constants
	const iterations = 10000
	const hashLength = 32 // SHA-256 produces a 32-byte hash

	// Result slice to store hashed passwords and salts
	results := make([][2]string, count)

	for i := 0; i < count; i++ {
		// Generate a random salt of the same length as the hash output
		salt := make([]byte, hashLength)
		_, err := rand.Read(salt)
		if err != nil {
			log.Printf("Error generating salt for user %s: %v\n", usernames[i], err)
			return nil
		}

		// Hash the password using PBKDF2-HMAC-SHA256
		hashedPassword := pbkdf2.Key([]byte(passwords[i]), salt, iterations, hashLength, sha256.New)

		// Convert the salt and hashed password to hexadecimal strings for storage
		saltHex := hex.EncodeToString(salt)
		hashedPasswordHex := hex.EncodeToString(hashedPassword)

		// Store the result as a tuple of hashed password and salt
		results[i] = [2]string{hashedPasswordHex, saltHex}
	}

	return results
}