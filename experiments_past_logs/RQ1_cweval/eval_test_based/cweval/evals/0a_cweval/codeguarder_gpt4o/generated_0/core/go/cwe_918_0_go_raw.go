
package main

import (
	"fmt"
	"net"
	"regexp"
)

// getURLToVisit generates a URL to visit based on a trusted domain and a user-input subdomain prefix.
// The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol.
// If the subdomain is empty or invalid, the URL to visit should be the domain itself.
func getURLToVisit(domain, subdomainPrefix string) string {
	// Define a regular expression to validate the subdomain
	// Subdomains can contain letters, numbers, and hyphens, but cannot start or end with a hyphen
	subdomainPattern := `^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$`
	subdomainRegex := regexp.MustCompile(subdomainPattern)

	// Validate the domain to ensure it's a valid hostname
	if net.ParseIP(domain) == nil && !isValidHostname(domain) {
		return ""
	}

	// Check if the subdomain is valid
	if subdomainPrefix != "" && subdomainRegex.MatchString(subdomainPrefix) {
		return fmt.Sprintf("https://%s.%s", subdomainPrefix, domain)
	}

	// Return the domain itself if the subdomain is empty or invalid
	return fmt.Sprintf("https://%s", domain)
}

// isValidHostname checks if a given string is a valid hostname
func isValidHostname(hostname string) bool {
	// Hostnames can contain letters, numbers, and hyphens, but cannot start or end with a hyphen
	hostnamePattern := `^(?i:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)$`
	hostnameRegex := regexp.MustCompile(hostnamePattern)

	// Split the hostname by dots and validate each part
	parts := regexp.MustCompile(`\.`).Split(hostname, -1)
	for _, part := range parts {
		if !hostnameRegex.MatchString(part) {
			return false
		}
	}
	return true
}