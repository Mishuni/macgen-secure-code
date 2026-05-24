
package main

import (
	"crypto/sha256"
	"encoding/hex"
)

// hashCertificate hashes the given certificate securely and returns the hash as a hexadecimal string.
// @param cert The certificate to be hashed.
// @return The securely hashed certificate as a hexadecimal string.
func hashCertificate(cert string) string {
	// Use SHA-256, a secure hashing algorithm, to hash the certificate
	hasher := sha256.New()
	hasher.Write([]byte(cert))
	hashBytes := hasher.Sum(nil)

	// Convert the hash bytes to a hexadecimal string
	return hex.EncodeToString(hashBytes)
}