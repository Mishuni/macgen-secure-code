package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"io"
	"os"
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

// BEGIN ENTRYPOINT
// Main function to read input from command line arguments, call the encryption function, and output the results
func main() {
	if len(os.Args) < 3 {
		fmt.Println("Usage: go run encryptData.go <key> <data>")
		os.Exit(1)
	}

	// Read key and data from command line arguments (hex format for both)
	key, err := hex.DecodeString(os.Args[1])
	if err != nil {
		fmt.Println("Error decoding key:", err)
		os.Exit(1)
	}

	data, err := hex.DecodeString(os.Args[2])
	if err != nil {
		fmt.Println("Error decoding data:", err)
		os.Exit(1)
	}

	// Encrypt the data
	encryptedData, iv, aesKey, err := encryptData(key, data)
	if err != nil {
		fmt.Println("Error encrypting data:", err)
		os.Exit(1)
	}

	// Print the results in hex format (compatible for Python parsing)
	fmt.Println(hex.EncodeToString(encryptedData))
	fmt.Println(hex.EncodeToString(iv))
	fmt.Println(hex.EncodeToString(aesKey))
}
