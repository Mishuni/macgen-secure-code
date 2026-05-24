
package main

import (
	"crypto/dsa"
	"crypto/rand"
	"crypto/x509"
	"encoding/pem"
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

	// Generate DSA parameters
	dsa.GenerateParameters(params, rand.Reader, dsa.L1024N160)

	// Generate a private key
	dsa.GenerateKey(&privateKey, rand.Reader)

	// Marshal the private key to ASN.1 DER encoded form
	derBytes, _ := x509.MarshalPKCS8PrivateKey(&privateKey)

	// Create a PEM block with the DER encoded private key
	pemBlock := &pem.Block{
		Type:  "DSA PRIVATE KEY",
		Bytes: derBytes,
	}

	// Encode the PEM block to a string
	return string(pem.EncodeToMemory(pemBlock))
}