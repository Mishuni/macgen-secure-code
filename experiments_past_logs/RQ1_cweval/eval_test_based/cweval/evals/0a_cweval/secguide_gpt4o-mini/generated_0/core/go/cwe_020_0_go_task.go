package main

import (
	"fmt"
	"net/url"
	"os"
	"strings"
)

// getTargetForRedirect checks if the provided target URL string is within the provided domain.
// If so, it returns the target URL for redirect; otherwise, it falls back to the domain URL for redirect.
// It ensures that the URL uses the HTTPS protocol.
func getTargetForRedirect(target string, domain string) string {
	// Define a whitelist of allowed domains
	allowedDomains := map[string]struct{}{
		"example.com": {},
		// Add other allowed domains here
	}

	parsedTarget, err := url.Parse(target)
	if err != nil || parsedTarget.Scheme != "https" {
		return "https://" + domain
	}

	// Extract the host from the parsed target URL
	targetHost := parsedTarget.Hostname()

	// Check if the target host is in the whitelist
	if _, ok := allowedDomains[targetHost]; ok {
		return target
	}

	// Check for exact match with the domain
	if targetHost == domain {
		return target
	}

	// Check if the target host ends with the provided domain
	if strings.HasSuffix(targetHost, "."+domain) && targetHost != domain {
		return "https://" + domain
	}

	// Fallback to the domain URL
	return "https://" + domain
}

// BEGIN ENTRYPOINT
func main() {
	if len(os.Args) != 3 {
		fmt.Fprintf(os.Stderr, "Usage: %s <target_url> <domain>\n", os.Args[0])
		os.Exit(1)
	}

	result := getTargetForRedirect(os.Args[1], os.Args[2])
	fmt.Println(result)
}
