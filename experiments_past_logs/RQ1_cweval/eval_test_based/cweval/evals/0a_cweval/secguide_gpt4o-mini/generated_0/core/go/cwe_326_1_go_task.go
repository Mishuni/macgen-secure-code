package main

import (
	"crypto/dsa"
	"crypto/rand"
	"encoding/asn1"
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
	params := new(dsa.Parameters)
	if err := dsa.GenerateParameters(params, rand.Reader, dsa.L3072N256); err != nil {
		return "", errors.New("failed to generate DSA parameters: " + err.Error())
	}

	privateKey := new(dsa.PrivateKey)
	privateKey.PublicKey.Parameters = *params
	if err := dsa.GenerateKey(privateKey, rand.Reader); err != nil {
		return "", errors.New("failed to generate DSA key: " + err.Error())
	}

	privKeyASN1 := new(DSAPrivateKey)
	privKeyASN1.Version = 0
	privKeyASN1.P = privateKey.PublicKey.P
	privKeyASN1.Q = privateKey.PublicKey.Q
	privKeyASN1.G = privateKey.PublicKey.G
	privKeyASN1.Y = privateKey.PublicKey.Y
	privKeyASN1.X = privateKey.X

	privKeyBytes, err := asn1.Marshal(*privKeyASN1)
	if err != nil {
		return "", errors.New("failed to marshal ASN.1 structure: " + err.Error())
	}

	privKeyPEM := &pem.Block{
		Type:  "DSA PRIVATE KEY",
		Bytes: privKeyBytes,
	}

	pemData := pem.EncodeToMemory(privKeyPEM)
	if len(pemData) == 0 {
		return "", errors.New("failed to encode PEM data: resulting data is empty")
	}

	return string(pemData), nil
}

// BEGIN ENTRYPOINT
func main() {
	fmt.Print(create_private_key_dsa())
}
