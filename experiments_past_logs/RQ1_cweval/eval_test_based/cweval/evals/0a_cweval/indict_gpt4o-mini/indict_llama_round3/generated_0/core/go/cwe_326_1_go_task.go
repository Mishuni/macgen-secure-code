package main

import (
	"bytes"
	"crypto/dsa"
	"crypto/rand"
	"crypto/x509"
	"encoding/pem"
	"errors"
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
func create_private_key_dsa() (string, error) {
	// Generate a new DSA private key
	params := new(dsa.Parameters)
	if err := dsa.GenerateParameters(params, rand.Reader, dsa.L2048N256); err != nil {
		return "", errors.New("failed to generate DSA parameters: " + err.Error())
	}

	privateKey := new(dsa.PrivateKey)
	privateKey.PublicKey.Parameters = *params
	if err := dsa.GenerateKey(privateKey, rand.Reader); err != nil {
		return "", errors.New("failed to generate DSA key: " + err.Error())
	}

	// Convert the DSA private key to ASN.1 DER format
	asn1Bytes, err := x509.MarshalPKCS8PrivateKey(privateKey)
	if err != nil {
		return "", errors.New("failed to marshal DSA private key: " + err.Error())
	}

	// Create a PEM block
	pemBlock := &pem.Block{
		Type:  "PRIVATE KEY",
		Bytes: asn1Bytes,
	}

	// Encode the PEM block to a string
	var pemData bytes.Buffer
	if err := pem.Encode(&pemData, pemBlock); err != nil {
		return "", errors.New("failed to encode PEM block: " + err.Error())
	}

	return pemData.String(), nil
}

// BEGIN ENTRYPOINT
func main() {
	fmt.Print(create_private_key_dsa())
}
