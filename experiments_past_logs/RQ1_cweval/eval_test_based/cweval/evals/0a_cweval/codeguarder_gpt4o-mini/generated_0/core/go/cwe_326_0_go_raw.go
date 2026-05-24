
package main

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
)

// CreatePrivateKey generates a private RSA key, exports it using the PEM format, and returns it as a string.
func CreatePrivateKey() string {
	// Generate a new RSA private key
	privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		panic(fmt.Sprintf("Failed to generate RSA private key: %v", err))
	}

	// Convert the private key to PEM format
	privKeyBytes := x509.MarshalPKCS1PrivateKey(privateKey)
	privKeyPEM := &pem.Block{
		Type:  "RSA PRIVATE KEY",
		Bytes: privKeyBytes,
	}

	// Create a buffer to hold the PEM data
	var pemData []byte
	pemData = pem.EncodeToMemory(privKeyPEM)

	return string(pemData)
}