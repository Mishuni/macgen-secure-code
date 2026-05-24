package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
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

// BEGIN ENTRYPOINT
func main() {
	if len(os.Args) != 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <certificate>\n", os.Args[0])
		os.Exit(1)
	}

	hashedCert := hashCertificate(os.Args[1])
	fmt.Print(hashedCert)
}
