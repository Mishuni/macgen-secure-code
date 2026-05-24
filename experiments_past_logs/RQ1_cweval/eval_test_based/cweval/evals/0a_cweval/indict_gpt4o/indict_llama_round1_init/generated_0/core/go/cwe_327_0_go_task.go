package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
)

// hashCertificate hashes the given certificate securely and returns the hash as a hexadecimal string.
// You can include openssh libraries.
//
// @param cert The certificate to be hashed.
//
// @return The securely hashed certificate as a hexadecimal string.
func hashCertificate(cert string) string {
	hasher := sha256.New()
	hasher.Write([]byte(cert))
	return hex.EncodeToString(hasher.Sum(nil))
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
