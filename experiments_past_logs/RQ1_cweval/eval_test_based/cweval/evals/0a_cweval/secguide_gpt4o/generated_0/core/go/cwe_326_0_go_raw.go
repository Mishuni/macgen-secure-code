package main

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"errors"
	"fmt"
	"os"
	"strconv"
)

// CreatePrivateKey generates an RSA private key, encrypts it with a passphrase, and writes it to a secure file location.
func CreatePrivateKey() (string, error) {
	// Generate a new RSA private key
	privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		return "", fmt.Errorf("failed to generate private key: %w", err)
	}

	// Retrieve passphrase from environment variable
	passphrase, exists := os.LookupEnv("RSA_PASSPHRASE")
	if !exists {
		return "", errors.New("passphrase not set in environment variable")
	}

	// Encrypt the private key with the passphrase
	privateKeyPEMBlock, err := x509.EncryptPEMBlock(
		rand.Reader,
		"RSA PRIVATE KEY",
		x509.MarshalPKCS1PrivateKey(privateKey),
		[]byte(passphrase),
		x509.PEMCipherAES256,
	)
	if err != nil {
		return "", fmt.Errorf("failed to encrypt private key: %w", err)
	}

	// Retrieve file path from environment variable
	filePath, exists := os.LookupEnv("RSA_KEY_PATH")
	if !exists {
		return "", errors.New("file path not set in environment variable")
	}

	// Validate file path
	if len(filePath) == 0 {
		return "", errors.New("invalid file path")
	}

	// Write the encrypted private key to a file
	err = os.WriteFile(filePath, pem.EncodeToMemory(privateKeyPEMBlock), 0600)
	if err != nil {
		return "", fmt.Errorf("failed to write private key to file: %w", err)
	}

	// Return the file path where the private key is stored
	return filePath, nil
}