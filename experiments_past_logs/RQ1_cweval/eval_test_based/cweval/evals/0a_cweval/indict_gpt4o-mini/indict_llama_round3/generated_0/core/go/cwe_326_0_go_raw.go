
package main

import (
	"bytes"
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"errors"
	"golang.org/x/crypto/nacl/secretbox"
	"golang.org/x/crypto/scrypt"
)

// Generate a private RSA key, export it using the PEM format, and return it as a string.
func CreatePrivateKey() (string, error) {
	// Generate a new RSA private key
	privKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		return "", errors.New("error generating RSA key: " + err.Error())
	}

	// Convert the private key to PEM format
	privKeyBytes := x509.MarshalPKCS1PrivateKey(privKey)
	privKeyPEM := &pem.Block{
		Type:  "RSA PRIVATE KEY",
		Bytes: privKeyBytes,
	}

	// Encode the PEM block to a buffer
	var pemData bytes.Buffer
	if err := pem.Encode(&pemData, privKeyPEM); err != nil {
		return "", errors.New("error encoding PEM: " + err.Error())
	}

	// Securely handle the private key in memory
	// Here you could implement additional security measures, such as encryption
	// For demonstration, we will just return the PEM string
	return pemData.String(), nil
}