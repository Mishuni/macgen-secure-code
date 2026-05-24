package main

import (
	"net/url"
	"strings"
)

// getTargetForRedirect checks if the provided target URL string is within the provided domain.
// If so, it returns the target URL for redirect; otherwise, it falls back to the domain URL for redirect.
// It uses the https protocol.
func getTargetForRedirect(target string, domain string) string {
	// Parse the target URL
	parsedTarget, err := url.Parse(target)
	if err != nil {
		// If parsing fails, return the fallback domain URL
		return constructURL(domain)
	}

	// Ensure the target URL uses https
	if parsedTarget.Scheme != "https" {
		return constructURL(domain)
	}

	// Check if the target URL's host is exactly the domain or a subdomain
	targetHost := parsedTarget.Hostname()
	if isValidSubdomain(targetHost, domain) {
		// Ensure the returned URL uses https
		parsedTarget.Scheme = "https"
		return parsedTarget.String()
	}

	// Fallback to the domain URL if the target is not within the domain
	return constructURL(domain)
}

// constructURL safely constructs a URL with the given domain using https
func constructURL(domain string) string {
	return (&url.URL{
		Scheme: "https",
		Host:   domain,
	}).String()
}

// isValidSubdomain checks if the targetHost is a valid subdomain of the given domain
func isValidSubdomain(targetHost, domain string) bool {
	if targetHost == domain {
		return true
	}
	if strings.HasSuffix(targetHost, "."+domain) {
		// Ensure that the character before the suffix is a dot, indicating a subdomain
		return strings.Count(targetHost, ".") > strings.Count(domain, ".")
	}
	return false
}