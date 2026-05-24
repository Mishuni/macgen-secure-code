package main

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"errors"
	"golang.org/x/crypto/scrypt"
	"io"
)

// Encrypt the data with the key using AES-256 in CBC mode.
// The provided key bytes should be a strong password or key material.
// Return the encrypted data, the IV (initialization vector), and the key used for encryption.
// Arguments:
// - key: The bytes to generate the encryption key.
// - data: The data to encrypt.
// Return:
// - The encrypted data, the IV, and the key used for encryption. (encryptedData, iv, aesKey, error)
func encryptData(key, data []byte) ([]byte, []byte, error) {
	if len(key) < 32 {
		return nil, nil, errors.New("key length must be at least 32 bytes for AES-256")
	}

	// Generate a unique salt for each encryption operation
	salt := make([]byte, 16)
	if _, err := io.ReadFull(rand.Reader, salt); err != nil {
		return nil, nil, err
	}

	// Derive a strong key from the provided key material using scrypt
	aesKey, err := scrypt.Key(key, salt, 16384, 8, 1, 32)
	if err != nil {
		return nil, nil, err
	}

	block, err := aes.NewCipher(aesKey)
	if err != nil {
		return nil, nil, err
	}

	// Create a new IV
	iv := make([]byte, aes.BlockSize)
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return nil, nil, err
	}

	// Check for zero-length data
	if len(data) == 0 {
		return nil, nil, errors.New("data length must be greater than zero")
	}

	// Pad the data to be a multiple of the block size using PKCS#7
	padding := aes.BlockSize - len(data)%aes.BlockSize
	padtext := bytes.Repeat([]byte{byte(padding)}, padding)
	data = append(data, padtext...)

	// Encrypt the data
	ciphertext := make([]byte, len(data))
	mode := cipher.NewCBCEncrypter(block, iv)
	mode.CryptBlocks(ciphertext, data)

	// Combine salt, iv, and ciphertext for storage
	encryptedData := append(salt, iv...)
	encryptedData = append(encryptedData, ciphertext...)

	return encryptedData, nil, nil
}