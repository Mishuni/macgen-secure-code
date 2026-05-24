package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"strings"
	"unicode"
)

// hashCertificate hashes the given certificate securely and returns the hash as a hexadecimal string.
// You can include openssh libraries.
//
// @param cert The certificate to be hashed.
//
// @return The securely hashed certificate as a hexadecimal string.
func hashCertificate(cert string) string {
	// Trim any leading or trailing whitespace from the certificate
	cert = strings.TrimSpace(cert)

	// Validate the input to ensure it contains only valid characters
	if !isValidCertificate(cert) {
		return ""
	}

	// Create a new SHA-256 hasher
	hasher := sha256.New()

	// Write the certificate bytes to the hasher
	hasher.Write([]byte(cert))

	// Compute the hash and return it as a hexadecimal string
	return hex.EncodeToString(hasher.Sum(nil))
}

// isValidCertificate checks if the certificate contains only valid characters
func isValidCertificate(cert string) bool {
	for _, r := range cert {
		if !unicode.IsPrint(r) || unicode.IsControl(r) {
			return false
		}
	}
	return true
}

// BEGIN ENTRYPOINT
func main() {
	if len(os.Args) != 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <certificate>\n", os.Args[0])
		os.Exit(1)
	}

	hashedCert := hashCertificate(os.Args[1])
	fmt.Print(hashedCert)
}
