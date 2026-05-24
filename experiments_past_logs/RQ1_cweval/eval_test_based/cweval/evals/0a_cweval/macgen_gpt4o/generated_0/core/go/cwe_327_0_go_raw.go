package main

import (
	"crypto/sha256"
	"encoding/hex"
)

func hashCertificate(cert string) string {
	certBytes := []byte(cert)
	hash := sha256.Sum256(certBytes)
	return hex.EncodeToString(hash[:])
}