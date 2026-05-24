package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/sha256"
	"errors"
	"fmt"
	"io"
)

func encryptData(key, data []byte) ([]byte, []byte, error) {
	// Validate the key length
	if len(key) != 32 {
		return nil, nil, errors.New("encryption key must be exactly 32 bytes long")
	}

	// Use SHA-256 to ensure the key is exactly 32 bytes
	aesKey := sha256.Sum256(key)

	block, err := aes.NewCipher(aesKey[:])
	if err != nil {
		return nil, nil, fmt.Errorf("failed to create cipher: %w", err)
	}

	// Generate a new nonce (12 bytes for GCM)
	nonce := make([]byte, 12)
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		return nil, nil, fmt.Errorf("failed to generate nonce: %w", err)
	}

	// Use GCM mode for encryption
	aesGCM, err := cipher.NewGCM(block)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to create GCM: %w", err)
	}

	// Encrypt the data
	encryptedData := aesGCM.Seal(nil, nonce, data, nil)

	return encryptedData, nonce, nil
}