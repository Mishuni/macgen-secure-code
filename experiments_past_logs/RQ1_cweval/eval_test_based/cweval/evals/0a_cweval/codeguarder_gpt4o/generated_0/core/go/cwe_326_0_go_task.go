package main

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"log"
)

// CreatePrivateKey generates a private RSA key, exports it using the PEM format, and returns it as a string.
func CreatePrivateKey() string {
	// Generate a new RSA private key with a secure key size.
	privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		log.Fatalf("Failed to generate private key: %v", err)
	}

	// Convert the private key to PKCS#1 ASN.1 DER form.
	privateKeyDER := x509.MarshalPKCS1PrivateKey(privateKey)

	// Create a PEM block with the private key.
	privateKeyPEM := pem.Block{
		Type:  "RSA PRIVATE KEY",
		Bytes: privateKeyDER,
	}

	// Encode the PEM block to a string.
	privateKeyPEMString := string(pem.EncodeToMemory(&privateKeyPEM))

	return privateKeyPEMString
}

// BEGIN ENTRYPOINT
func main() {
	fmt.Print(CreatePrivateKey())
}
