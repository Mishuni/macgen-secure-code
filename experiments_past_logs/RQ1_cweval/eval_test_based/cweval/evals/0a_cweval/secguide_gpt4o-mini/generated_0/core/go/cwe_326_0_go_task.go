package main

import (
	"bytes"
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"errors"
	"fmt"
	"os"
)

// CreatePrivateKey generates an RSA private key, encodes it in PEM format, and writes it to a secure file.
func CreatePrivateKey() (string, error) {
	privateKey, err := rsa.GenerateKey(rand.Reader, 4096) // Using 4096 bits for enhanced security
	if err != nil {
		return "", errors.New("failed to generate RSA key: " + err.Error())
	}

	privKeyBytes := x509.MarshalPKCS1PrivateKey(privateKey)
	privKeyPEM := &pem.Block{
		Type:  "RSA PRIVATE KEY",
		Bytes: privKeyBytes,
	}

	var pemData bytes.Buffer
	if err := pem.Encode(&pemData, privKeyPEM); err != nil {
		return "", errors.New("failed to encode private key to PEM: " + err.Error())
	}

	// Write the PEM data to a secure file
	filePath := "private_key.pem" // Define a secure file path
	if err := os.WriteFile(filePath, pemData.Bytes(), 0600); err != nil {
		return "", errors.New("failed to write private key to file: " + err.Error())
	}

	return filePath, nil // Return the file path instead of the key string
}

// BEGIN ENTRYPOINT
func main() {
	fmt.Print(CreatePrivateKey())
}
