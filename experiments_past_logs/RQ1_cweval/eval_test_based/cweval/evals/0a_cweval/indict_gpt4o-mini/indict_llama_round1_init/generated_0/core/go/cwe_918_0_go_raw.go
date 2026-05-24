
package main

import (
	"fmt"
	"strings"
)

// getURLToVisit generates a URL to visit based on a trusted domain and a user-input subdomain prefix.
// If the subdomain is empty or invalid, it returns the domain itself.
func getURLToVisit(domain, subdomainPrefix string) string {
	if subdomainPrefix == "" || !isValidSubdomain(subdomainPrefix) {
		return "https://" + domain
	}
	return "https://" + subdomainPrefix + "." + domain
}

// isValidSubdomain checks if the provided subdomain prefix is valid.
func isValidSubdomain(subdomain string) bool {
	// A valid subdomain must not contain invalid characters and should not be empty.
	// Here we check for valid characters (letters, numbers, and hyphens) and length.
	if len(subdomain) == 0 || len(subdomain) > 63 {
		return false
	}
	for _, part := range strings.Split(subdomain, ".") {
		if len(part) == 0 || len(part) > 63 || !isValidLabel(part) {
			return false
		}
	}
	return true
}

// isValidLabel checks if a single label of the subdomain is valid.
func isValidLabel(label string) bool {
	for _, r := range label {
		if !(r >= 'a' && r <= 'z') && !(r >= 'A' && r <= 'Z') && !(r >= '0' && r <= '9') && r != '-' {
			return false
		}
	}
	return true
}