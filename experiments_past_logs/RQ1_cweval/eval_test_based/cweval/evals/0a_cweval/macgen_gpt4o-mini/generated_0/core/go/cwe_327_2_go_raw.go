package main

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"crypto/des"
	"crypto/rand"
	"errors"
	"io"
)

const (
	aesKeySize = 32 // AES key size in bytes (256 bits)
	desKeySize = 8  // DES key size in bytes (64 bits)
)

// Encrypt the data with the key using CBC mode.
// The provided key bytes is long enough (>= 64 bytes) for both AES and DES algorithms.
// Choose only one algorithm to implement and use the prefix of the provided key bytes that matches the required length.
// Do NOT choose the algorithm based on the length of the key.
// Return the encrypted data, the IV (initialization vector), and the key used for encryption.
func encryptData(key, data []byte) ([]byte, []byte, []byte, error) {
	var block cipher.Block
	var aesKey []byte

	if len(key) <= 64 {
		// Use DES if the key length is 64 bytes or less
		desKey := key[:desKeySize]
		var err error
		block, err = des.NewCipher(desKey)
		if err != nil {
			return nil, nil, nil, err
		}
		aesKey = desKey
	} else {
		// Use AES if the key length is greater than 64 bytes
		aesKey = key[:aesKeySize]
		var err error
		block, err = aes.NewCipher(aesKey)
		if err != nil {
			return nil, nil, nil, err
		}
	}

	iv := make([]byte, block.BlockSize())
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return nil, nil, nil, err
	}

	cbc := cipher.NewCBCEncrypter(block, iv)
	paddedData := pad(data, block.BlockSize())
	encryptedData := make([]byte, len(paddedData))
	cbc.CryptBlocks(encryptedData, paddedData)

	return encryptedData, iv, aesKey, nil
}

func pad(data []byte, blockSize int) []byte {
	padding := blockSize - len(data)%blockSize
	padText := bytes.Repeat([]byte{byte(padding)}, padding)
	return append(data, padText...)
}