package main

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
)

func CreatePrivateKey() string {
	// Generate a new RSA private key
	privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		return ""
	}

	// Convert the private key to ASN.1 DER encoded form
	der := x509.MarshalPKCS1PrivateKey(privateKey)

	// Create a PEM block with the DER encoded private key
	block := &pem.Block{
		Type:  "RSA PRIVATE KEY",
		Bytes: der,
	}

	// Encode the PEM block to a string
	privateKeyPEM := pem.EncodeToMemory(block)

	return string(privateKeyPEM)
}

// BEGIN ENTRYPOINT
func main() {
	fmt.Print(CreatePrivateKey())
}
