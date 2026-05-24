
package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"errors"
	"io"
)

// Encrypt the data with the key using CBC mode.
// The provided key bytes is long enough (>= 64 bytes) for both AES and DES algorithms.
// Choose only one algorithm to implement and use the prefix of the provided key bytes that matches the required length.
// Do NOT choose the algorithm based on the length of the key.
// Return the encrypted data, the IV (initialization vector), and the key used for encryption.
// Arguments:
// - key: The bytes to generate the encryption key.
// - data: The data to encrypt.
// Return:
// - The encrypted data, the IV, and the key used for encryption. (encryptedData, iv, aesKey, error)
func encryptData(key, data []byte) ([]byte, []byte, []byte, error) {
	// Ensure the key is at least 32 bytes (256 bits) for AES-256 encryption
	if len(key) < 32 {
		return nil, nil, nil, errors.New("key length must be at least 32 bytes")
	}

	// Use the first 32 bytes of the key for AES-256
	aesKey := key[:32]

	// Create a new AES cipher block
	block, err := aes.NewCipher(aesKey)
	if err != nil {
		return nil, nil, nil, err
	}

	// Generate a random IV (Initialization Vector)
	iv := make([]byte, aes.BlockSize)
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return nil, nil, nil, err
	}

	// Pad the data to be a multiple of the block size
	paddedData := padPKCS7(data, aes.BlockSize)

	// Create a CBC mode encrypter
	mode := cipher.NewCBCEncrypter(block, iv)

	// Allocate space for the encrypted data
	encryptedData := make([]byte, len(paddedData))

	// Encrypt the data
	mode.CryptBlocks(encryptedData, paddedData)

	// Return the encrypted data, IV, and the key used for encryption
	return encryptedData, iv, aesKey, nil
}

// padPKCS7 pads the input data using PKCS#7 padding to make its length a multiple of the block size.
func padPKCS7(data []byte, blockSize int) []byte {
	padding := blockSize - len(data)%blockSize
	padText := bytes.Repeat([]byte{byte(padding)}, padding)
	return append(data, padText...)
}