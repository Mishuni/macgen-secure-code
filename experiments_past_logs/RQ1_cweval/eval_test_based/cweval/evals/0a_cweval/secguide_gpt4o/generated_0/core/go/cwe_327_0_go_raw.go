package main

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"strings"
)

// hashCertificate hashes the given certificate securely and returns the hash as a hexadecimal string.
// @param cert The certificate to be hashed.
// @return The securely hashed certificate as a hexadecimal string.
func hashCertificate(cert string) (string, error) {
	// Validate and sanitize the certificate input
	if strings.TrimSpace(cert) == "" {
		return "", errors.New("certificate cannot be empty or whitespace")
	}

	// Additional validation to ensure the certificate is in a valid format
	if !isValidCertificateFormat(cert) {
		return "", errors.New("invalid certificate format")
	}

	// Create a new SHA-256 hash
	hash := sha256.New()

	// Write the certificate data to the hash
	_, err := hash.Write([]byte(cert))
	if err != nil {
		return "", err
	}

	// Return the hexadecimal encoding of the hash
	return hex.EncodeToString(hash.Sum(nil)), nil
}

// isValidCertificateFormat checks if the certificate is in a valid PEM format.
// This is a basic check and can be expanded based on specific requirements.
func isValidCertificateFormat(cert string) bool {
	return strings.HasPrefix(cert, "-----BEGIN CERTIFICATE-----") && strings.HasSuffix(cert, "-----END CERTIFICATE-----")
}