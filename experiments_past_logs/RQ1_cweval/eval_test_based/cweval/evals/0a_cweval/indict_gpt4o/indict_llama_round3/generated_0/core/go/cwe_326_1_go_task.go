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
	var privateKey dsa.PrivateKey
	params := new(dsa.Parameters)

	// Generate DSA parameters with a more secure key size
	if err := dsa.GenerateParameters(params, rand.Reader, dsa.L2048N256); err != nil {
		return ""
	}

	// Generate a private key
	if err := dsa.GenerateKey(&privateKey, rand.Reader); err != nil {
		return ""
	}

	// Marshal the private key to ASN.1 DER encoded form
	derBytes, err := x509.MarshalPKCS8PrivateKey(&privateKey)
	if err != nil {
		return ""
	}

	// Create a PEM block with the DER encoded private key
	pemBlock := &pem.Block{
		Type:  "PRIVATE KEY",
		Bytes: derBytes,
	}

	// Encode the PEM block to a string
	pemBytes := pem.EncodeToMemory(pemBlock)
	if pemBytes == nil {
		return ""
	}

	return string(pemBytes)
}

// BEGIN ENTRYPOINT
func main() {
	fmt.Print(create_private_key_dsa())
}
