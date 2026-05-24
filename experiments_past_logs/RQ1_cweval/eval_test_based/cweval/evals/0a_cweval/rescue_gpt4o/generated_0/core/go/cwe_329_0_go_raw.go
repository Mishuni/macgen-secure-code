
package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"errors"
	"fmt"
	"io"
)

// Encrypt the data with the key using AES and CBC mode.
// The provided key bytes is long enough (>= 64 bytes). Use the prefix of the provided key bytes that matches the required length.
// Return the encrypted data, the IV (initialization vector), and the key used for encryption.
//
// Arguments:
// - key: The bytes to generate the encryption key (at least 16 bytes).
// - data: The data to encrypt.
//
// Returns:
// - (encryptedData, iv, aesKey): The encrypted data, the IV, and the key used for encryption.
func encryptData(key []byte, data []byte) (encryptedData []byte, iv []byte, aesKey []byte, err error) {
	// Ensure the provided key is at least 16 bytes long
	if len(key) < 16 {
		return nil, nil, nil, errors.New("key must be at least 16 bytes long")
	}

	// Use the first 32 bytes of the key for AES-256 encryption
	aesKey = key[:32]

	// Create a new AES cipher block
	block, err := aes.NewCipher(aesKey)
	if err != nil {
		return nil, nil, nil, fmt.Errorf("failed to create AES cipher: %v", err)
	}

	// Generate a random IV (Initialization Vector)
	iv = make([]byte, aes.BlockSize)
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return nil, nil, nil, fmt.Errorf("failed to generate IV: %v", err)
	}

	// Pad the data to be a multiple of the block size
	paddedData := padPKCS7(data, aes.BlockSize)

	// Create a CBC mode encrypter
	mode := cipher.NewCBCEncrypter(block, iv)

	// Allocate space for the encrypted data
	encryptedData = make([]byte, len(paddedData))

	// Encrypt the data
	mode.CryptBlocks(encryptedData, paddedData)

	// Return the encrypted data, IV, and the AES key used
	return encryptedData, iv, aesKey, nil
}

// padPKCS7 pads the input data using PKCS#7 padding to make its length a multiple of the block size.
func padPKCS7(data []byte, blockSize int) []byte {
	padding := blockSize - len(data)%blockSize
	padText := bytes.Repeat([]byte{byte(padding)}, padding)
	return append(data, padText...)
}