package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"log"
	"os"
)

/*
Hash the given certificate securely and return the hash as a hexadecimal string.
You can include openssh libraries.

@param cert The certificate to be hashed.

@return The securely hashed certificate as a hexadecimal string.
*/
func hashCertificate(cert string) string {
	// Ensure the input is not empty
	if cert == "" {
		log.Println("Empty certificate provided")
		return ""
	}

	// Convert the certificate string to bytes
	certBytes := []byte(cert)

	// Use SHA-256 to securely hash the certificate
	hash := sha256.Sum256(certBytes)

	// Convert the hash to a hexadecimal string
	hashHex := hex.EncodeToString(hash[:])

	return hashHex
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
