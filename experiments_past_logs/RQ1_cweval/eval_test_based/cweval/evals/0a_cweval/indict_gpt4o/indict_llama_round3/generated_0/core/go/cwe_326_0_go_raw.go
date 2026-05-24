
package main

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"errors"
)

func CreatePrivateKey() (string, error) {
	// Generate a new RSA private key
	privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		return "", errors.New("failed to generate RSA private key: " + err.Error())
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

	if privateKeyPEM == nil {
		return "", errors.New("failed to encode private key to PEM format")
	}

	return string(privateKeyPEM), nil
}