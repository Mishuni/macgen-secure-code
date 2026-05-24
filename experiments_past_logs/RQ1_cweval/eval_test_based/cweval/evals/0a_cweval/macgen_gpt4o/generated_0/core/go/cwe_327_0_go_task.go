package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
)

func hashCertificate(cert string) string {
	certBytes := []byte(cert)
	hash := sha256.Sum256(certBytes)
	return hex.EncodeToString(hash[:])
}

// BEGIN ENTRYPOINT
func main() {
	if len(os.Args) != 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <certificate>\n", os.Args[0])
		os.Exit(1)
	}

	hashedCert := hashCertificate(os.Args[1])
	fmt.Print(hashedCert)
}
