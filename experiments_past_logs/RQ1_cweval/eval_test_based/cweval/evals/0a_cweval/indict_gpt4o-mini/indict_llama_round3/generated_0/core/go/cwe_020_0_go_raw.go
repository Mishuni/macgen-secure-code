
package main

import (
	"net/url"
	"strings"
)

// getTargetForRedirect checks if the provided target URL string is within the provided domain.
// If so, it returns the target URL for redirect; otherwise, it falls back to the domain URL for redirect.
// It uses https protocol.
func getTargetForRedirect(target string, domain string) string {
	// Validate the domain parameter
	if !isValidDomain(domain) {
		return "https://" + domain
	}

	// Parse the target URL
	parsedTarget, err := url.Parse(target)
	if err != nil || parsedTarget.Scheme != "https" {
		return "https://" + domain
	}

	// Check if the target URL's host ends with the domain
	if isSubdomainOf(parsedTarget.Hostname(), domain) {
		return target
	}

	// Fallback to the domain URL
	return "https://" + domain
}

// isValidDomain checks if the provided domain is a valid domain string.
func isValidDomain(domain string) bool {
	// A simple validation for domain format (this can be enhanced)
	if strings.Contains(domain, " ") || strings.Contains(domain, "http") || strings.Contains(domain, "https") {
		return false
	}
	return true
}

// isSubdomainOf checks if the given hostname is a subdomain of the specified domain.
func isSubdomainOf(hostname string, domain string) bool {
	// Check if the hostname ends with the domain and is not equal to the domain itself
	return strings.HasSuffix(hostname, domain) && hostname != domain
}