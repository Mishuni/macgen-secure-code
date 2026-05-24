package main

import (
	"crypto/sha256"
	"encoding/hex"
	"strings"
)

func hashCertificate(cert string) string {
	cert = strings.TrimSpace(cert)
	if cert == "" {
		return "error: empty certificate"
	}

	hash := sha256.New()
	_, err := hash.Write([]byte(cert))
	if err != nil {
		return "error: hashing failed"
	}
	return hex.EncodeToString(hash.Sum(nil))
}