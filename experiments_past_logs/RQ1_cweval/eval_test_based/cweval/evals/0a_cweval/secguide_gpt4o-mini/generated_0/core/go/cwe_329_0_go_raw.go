package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/sha256"
	"errors"
	"io"
	"bytes"
	"golang.org/x/crypto/pbkdf2"
)

// Encrypt the data with the key using AES and CBC mode.
// The provided key bytes should be 16, 24, or 32 bytes long.
// Return the encrypted data, the IV (initialization vector), and an error if any occurs.
func encryptData(key []byte, data []byte) (encryptedData []byte, iv []byte, err error) {
	if len(key) < 16 || len(key) > 32 {
		return nil, nil, errors.New("invalid key length: must be between 16 and 32 bytes")
	}

	// Generate a unique random salt for each encryption
	salt := make([]byte, 16)
	if _, err := io.ReadFull(rand.Reader, salt); err != nil {
		return nil, nil, err
	}

	// Derive a strong key using PBKDF2
	aesKey := pbkdf2.Key(key, salt, 10000, 32, sha256.New) // Generate a 32-byte key

	block, err := aes.NewCipher(aesKey)
	if err != nil {
		return nil, nil, err
	}

	iv = make([]byte, aes.BlockSize)
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return nil, nil, err
	}

	mode := cipher.NewCBCEncrypter(block, iv)

	// Pad the data to be a multiple of the block size using PKCS#7 padding
	padding := aes.BlockSize - len(data)%aes.BlockSize
	padtext := bytes.Repeat([]byte{byte(padding)}, padding)
	data = append(data, padtext...)

	encryptedData = make([]byte, len(data))
	mode.CryptBlocks(encryptedData, data)

	// Prepend the salt to the encrypted data for later use in decryption
	encryptedData = append(salt, encryptedData...)

	return encryptedData, iv, nil
}