
package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"os"
)

// Encrypt the data with the key using AES and CBC mode.
// The provided key bytes is long enough (>= 64 bytes). Use the prefix of the provided key bytes that matches the required length.
// Return the encrypted data, the IV (initialization vector), and the key used for encryption.
func encryptData(key []byte, data []byte) (encryptedData []byte, iv []byte, aesKey []byte) {
	// Ensure the key length is at least 16 bytes for AES
	if len(key) < 16 {
		return nil, nil, nil
	}

	// Use the first 16 bytes of the key for AES-128
	aesKey = key[:16]

	// Create a new AES cipher
	block, err := aes.NewCipher(aesKey)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error creating AES cipher: %v\n", err)
		return nil, nil, nil
	}

	// Generate a new IV
	iv = make([]byte, aes.BlockSize)
	if _, err := rand.Read(iv); err != nil {
		fmt.Fprintf(os.Stderr, "Error generating IV: %v\n", err)
		return nil, nil, nil
	}

	// Create a new CBC encrypter
	mode := cipher.NewCBCEncrypter(block, iv)

	// Pad the data to be a multiple of the block size
	padding := aes.BlockSize - len(data)%aes.BlockSize
	padtext := append(data, bytes.Repeat([]byte{byte(padding)}, padding)...)

	// Encrypt the data
	encryptedData = make([]byte, len(padtext))
	mode.CryptBlocks(encryptedData, padtext)

	return encryptedData, iv, aesKey
}