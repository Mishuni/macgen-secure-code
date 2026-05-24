
package main

import (
	"crypto/sha256"
	"encoding/hex"
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