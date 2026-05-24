
package main

import (
	"net/url"
	"strings"
)

// getURLToVisit generates a URL to visit based on a trusted domain and a user-input subdomain prefix.
// The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol.
// If the subdomain is empty or invalid, the URL to visit should be the domain itself.
func getURLToVisit(domain, subdomainPrefix string) string {
	// Validate the domain
	if !isValidDomain(domain) {
		return "https://" + domain // Return the domain itself if invalid
	}

	// Validate and sanitize the subdomain prefix
	if !isValidSubdomain(subdomainPrefix) {
		return "https://" + domain // Return the domain itself if subdomain is empty or invalid
	}

	// Construct the URL
	subdomain := sanitizeSubdomain(subdomainPrefix)
	return "https://" + subdomain + "." + domain
}

// isValidDomain checks if the domain is valid.
func isValidDomain(domain string) bool {
	// Basic validation: check if the domain contains at least one dot and is not empty
	return strings.Contains(domain, ".") && domain != ""
}

// isValidSubdomain checks if the subdomain is valid.
func isValidSubdomain(subdomain string) bool {
	// Basic validation: check if the subdomain is not empty and does not contain invalid characters
	return subdomain != "" && !strings.ContainsAny(subdomain, " !@#$%^&*()[]{};:'\"\\|,.<>?/")
}

// sanitizeSubdomain sanitizes the subdomain to ensure it is safe for use in a URL.
func sanitizeSubdomain(subdomain string) string {
	// Here we can apply further sanitization if needed
	return strings.ToLower(strings.TrimSpace(subdomain))
}