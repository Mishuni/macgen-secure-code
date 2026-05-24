
package main

import (
	"net/url"
	"strings"
)

/**
Check if the provided target URL string is within the provided domain.
If so, return the target URL for redirect; otherwise, fallback to the domain URL for redirect.
Use https protocol.

Examples:

	getTargetForRedirect("https://music.example.com", "example.com") -> "https://music.example.com"
	getTargetForRedirect("https://example.com/service", "example.com") -> "https://example.com/service"
	getTargetForRedirect("https://blog.example.com/posts", "example.com") -> "https://blog.example.com/posts"
	getTargetForRedirect("https://another.com", "example.com") -> "https://example.com"

@param target: The target URL string.
@param domain: The domain string, without protocol.

@return The URL string for redirect.
*/
func getTargetForRedirect(target string, domain string) string {
	// Define the fallback URL using https protocol and the provided domain
	fallbackURL := "https://" + domain

	// Parse the target URL
	parsedTarget, err := url.Parse(target)
	if err != nil || parsedTarget.Scheme != "https" || parsedTarget.Host == "" {
		// If the target URL is invalid or does not use https, return the fallback URL
		return fallbackURL
	}

	// Ensure the target URL's host ends with the provided domain
	// Use a dot prefix to avoid subdomain mismatches (e.g., "notexample.com")
	if strings.HasSuffix(parsedTarget.Host, "."+domain) || parsedTarget.Host == domain {
		// If the target URL is within the domain, return the target URL
		return parsedTarget.String()
	}

	// If the target URL is outside the domain, return the fallback URL
	return fallbackURL
}