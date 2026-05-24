
package main

import (
	"crypto/x509"
	"encoding/hex"
	"errors"
	"strings"
)

// hashCertificate securely hashes the given certificate and returns the hash as a hexadecimal string.
// @param cert The certificate to be hashed.
// @return The securely hashed certificate as a hexadecimal string.
func hashCertificate(cert string) (string, error) {
	// Input validation: Check for empty certificate
	if strings.TrimSpace(cert) == "" {
		return "", errors.New("certificate cannot be empty")
	}

	// Parse the certificate to ensure it is well-formed
	block, rest := pem.Decode([]byte(cert))
	if block == nil || len(rest) > 0 {
		return "", errors.New("invalid certificate format")
	}

	certificate, err := x509.ParseCertificate(block.Bytes)
	if err != nil {
		return "", errors.New("failed to parse certificate: " + err.Error())
	}

	// Hash the certificate using SHA-256
	hash := sha256.New()
	hash.Write(certificate.Raw) // Use the raw bytes of the certificate for hashing
	return hex.EncodeToString(hash.Sum(nil)), nil
}