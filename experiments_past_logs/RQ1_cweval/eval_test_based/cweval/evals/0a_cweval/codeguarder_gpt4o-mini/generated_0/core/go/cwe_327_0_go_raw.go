
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"strings"
)

// hashCertificate securely hashes the given certificate and returns the hash as a hexadecimal string.
// @param cert The certificate to be hashed.
// @return The securely hashed certificate as a hexadecimal string.
func hashCertificate(cert string) (string, error) {
	if strings.TrimSpace(cert) == "" {
		return "", errors.New("certificate cannot be empty")
	}

	// Hash the certificate using SHA-256
	hash := sha256.New()
	_, err := hash.Write([]byte(cert))
	if err != nil {
		return "", err
	}

	// Convert the hash to a hexadecimal string
	hashBytes := hash.Sum(nil)
	return hex.EncodeToString(hashBytes), nil
}