
package main

import (
	"net/url"
	"strings"
)

// getTargetForRedirect checks if the provided target URL string is within the provided domain.
// If so, it returns the target URL for redirect; otherwise, it falls back to the domain URL for redirect.
// It uses the https protocol.
func getTargetForRedirect(target string, domain string) string {
	parsedTarget, err := url.Parse(target)
	if err != nil {
		// If the target URL is invalid, fallback to the domain URL
		return "https://" + domain
	}

	// Ensure the target URL uses https
	if parsedTarget.Scheme != "https" {
		parsedTarget.Scheme = "https"
	}

	// Check if the target URL's host ends with the provided domain
	if strings.HasSuffix(parsedTarget.Hostname(), domain) {
		return parsedTarget.String()
	}

	// Fallback to the domain URL if the target is not within the provided domain
	return "https://" + domain
}