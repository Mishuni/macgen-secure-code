
package main

import (
	"crypto/dsa"
	"crypto/rand"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"math/big"
)

// DSAPrivateKey represents ASN.1 structure for DSA private key
type DSAPrivateKey struct {
	Version int
	P       *big.Int
	Q       *big.Int
	G       *big.Int
	Y       *big.Int
	X       *big.Int
}

// Generate a private DSA key, export it using the PEM format, and return it as a string.
//
// Returns:
//
//	string: The DSA private key in PEM format.
func create_private_key_dsa() string {
	// Generate a new DSA key
	params := new(dsa.Parameters)
	if err := dsa.GenerateParameters(params, rand.Reader, dsa.L2048N256); err != nil {
		return ""
	}

	privateKey := new(dsa.PrivateKey)
	privateKey.PublicKey.Parameters = *params
	if err := dsa.GenerateKey(privateKey, rand.Reader); err != nil {
		return ""
	}

	// Marshal the private key to ASN.1 DER format
	privDER := x509.MarshalPKCS8PrivateKey(privateKey)

	// Create a PEM block
	pemBlock := &pem.Block{
		Type:  "PRIVATE KEY",
		Bytes: privDER,
	}

	// Encode the PEM block to a string
	var pemData []byte
	pemData = pem.EncodeToMemory(pemBlock)

	return string(pemData)
}