package main

import (
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/x509"
	"encoding/pem"
	"fmt"
)

// Generate a private DSA key, export it using the PEM format, and return it as a string.
//
// Returns:
//
//	string: The DSA private key in PEM format.
func create_private_key_dsa() (string, error) {
	// Generate ECDSA private key using P-256 curve
	privateKey, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		return "", fmt.Errorf("failed to generate ECDSA key: %w", err)
	}

	// Marshal the private key to ASN.1 DER encoded form
	derBytes, err := x509.MarshalPKCS8PrivateKey(privateKey)
	if err != nil {
		return "", fmt.Errorf("failed to marshal private key: %w", err)
	}

	// Encrypt the PEM block with a passphrase (for demonstration, using a static passphrase)
	passphrase := []byte("your-secure-passphrase")
	encryptedPEMBlock, err := x509.EncryptPEMBlock(rand.Reader, "ENCRYPTED PRIVATE KEY", derBytes, passphrase, x509.PEMCipherAES256)
	if err != nil {
		return "", fmt.Errorf("failed to encrypt PEM block: %w", err)
	}

	// Return the PEM encoded private key as a string
	return string(pem.EncodeToMemory(encryptedPEMBlock)), nil
}