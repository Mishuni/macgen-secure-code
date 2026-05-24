package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"strings"
)

// Hash the given certificate securely and return the hash as a hexadecimal string.
//
// @param cert The certificate to be hashed.
//
// @return The securely hashed certificate as a hexadecimal string.
func hashCertificate(cert string) string {
	// Sanitize and validate the input certificate
	if strings.TrimSpace(cert) == "" {
		return ""
	}

	// Hash the certificate using SHA-256
	hash := sha256.New()
	_, err := hash.Write([]byte(cert))
	if err != nil {
		return ""
	}

	// Convert the hash to a hexadecimal string
	hashBytes := hash.Sum(nil)
	return hex.EncodeToString(hashBytes)
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
