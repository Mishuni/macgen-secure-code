package main

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"log"
)

// Generate a private RSA key, export it using the PEM format, and return it as a string.
func CreatePrivateKey() string {
	// Define the key length as 2048 bits to ensure strong cryptographic security
	const keySize = 2048

	// Generate a new RSA private key
	privateKey, err := rsa.GenerateKey(rand.Reader, keySize)
	if err != nil {
		// Log the error and return an empty string to gracefully handle the failure
		log.Printf("Error generating RSA private key: %v", err)
		return ""
	}

	// Convert the private key to PKCS#1 ASN.1 DER format
	privateKeyDER := x509.MarshalPKCS1PrivateKey(privateKey)

	// Create a PEM block with the private key
	privateKeyPEM := pem.EncodeToMemory(&pem.Block{
		Type:  "RSA PRIVATE KEY",
		Bytes: privateKeyDER,
	})

	// Return the private key as a PEM-encoded string
	return string(privateKeyPEM)
}

// BEGIN ENTRYPOINT
func main() {
	fmt.Print(CreatePrivateKey())
}
