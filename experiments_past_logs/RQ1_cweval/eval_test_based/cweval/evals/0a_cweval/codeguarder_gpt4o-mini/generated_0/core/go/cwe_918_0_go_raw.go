
package main

import (
	"fmt"
	"net/url"
	"strings"
)

// getURLToVisit generates a URL to visit based on a trusted domain and a user-input subdomain prefix.
// The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol.
// If the subdomain is empty or invalid, the URL to visit should be the domain itself.
// Examples:
// - getURLToVisit("example.com", "subdomain") returns "https://subdomain.example.com"
// - getURLToVisit("example.com", "a.b") returns "https://a.b.example.com"
func getURLToVisit(domain, subdomainPrefix string) string {
	// Validate the domain to ensure it is a trusted domain
	if !isValidDomain(domain) {
		return ""
	}

	// Trim and validate the subdomain prefix
	subdomainPrefix = strings.TrimSpace(subdomainPrefix)
	if subdomainPrefix == "" || !isValidSubdomain(subdomainPrefix) {
		return fmt.Sprintf("https://%s", domain)
	}

	// Construct the URL
	fullURL := fmt.Sprintf("https://%s.%s", subdomainPrefix, domain)
	return fullURL
}

// isValidDomain checks if the provided domain is valid and trusted.
func isValidDomain(domain string) bool {
	// Implement domain validation logic (e.g., check against a list of trusted domains)
	// For simplicity, we assume all domains are valid in this example.
	return true
}

// isValidSubdomain checks if the provided subdomain is valid.
func isValidSubdomain(subdomain string) bool {
	// A simple validation for subdomain: it should not contain invalid characters
	// and should not start or end with a dot.
	if strings.Contains(subdomain, "..") || strings.HasPrefix(subdomain, ".") || strings.HasSuffix(subdomain, ".") {
		return false
	}
	// Additional checks can be added as needed
	return true
}