package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"errors"
	"fmt"
	"io"
)

// encryptData encrypts the given data using AES-128 in GCM mode.
// It requires a 16-byte key and returns the encrypted data, nonce, and any error encountered.
func encryptData(key []byte, data []byte) (encryptedData []byte, nonce []byte, err error) {
	// Ensure the key is exactly 16 bytes long for AES-128
	if len(key) != 16 {
		return nil, nil, errors.New("key must be exactly 16 bytes long")
	}

	// Create a new AES cipher block
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to create AES cipher block: %w", err)
	}

	// Create a new GCM cipher mode
	aesGCM, err := cipher.NewGCM(block)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to create GCM cipher mode: %w", err)
	}

	// Generate a new nonce
	nonce = make([]byte, aesGCM.NonceSize())
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		return nil, nil, fmt.Errorf("failed to generate nonce: %w", err)
	}

	// Encrypt the data
	encryptedData = aesGCM.Seal(nil, nonce, data, nil)

	return encryptedData, nonce, nil
}