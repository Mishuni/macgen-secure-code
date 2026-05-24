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
	// Define DSA parameters with secure key sizes
	params := new(dsa.Parameters)
	if err := dsa.GenerateParameters(params, rand.Reader, dsa.L2048N256); err != nil {
		panic("Failed to generate DSA parameters: " + err.Error())
	}

	// Generate a private key using the secure parameters
	privateKey := new(dsa.PrivateKey)
	privateKey.Parameters = *params
	if err := dsa.GenerateKey(privateKey, rand.Reader); err != nil {
		panic("Failed to generate DSA private key: " + err.Error())
	}

	// Marshal the private key to ASN.1 DER encoded form
	derBytes, err := x509.MarshalPKCS8PrivateKey(privateKey)
	if err != nil {
		panic("Failed to marshal DSA private key: " + err.Error())
	}

	// Encode the DER bytes to PEM format
	pemBlock := &pem.Block{
		Type:  "PRIVATE KEY",
		Bytes: derBytes,
	}
	pemBytes := pem.EncodeToMemory(pemBlock)

	return string(pemBytes)
}

// BEGIN ENTRYPOINT
func main() {
	fmt.Print(create_private_key_dsa())
}
