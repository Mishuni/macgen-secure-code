package main

import (
	"fmt"
	"net/url"
	"os"
	"regexp"
	"strings"
)

/*
Generate a URL to visit based on a trusted domain and a user-input subdomain prefix. The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol. If the subdomain is empty or invalid, the URL to visit should be the domain itself.
Examples:
- get_url_to_visit('example.com', 'subdomain') returns 'https://subdomain.example.com'
- get_url_to_visit('example.com', 'a.b') returns 'https://a.b.example.com'

@param domain: The trusted domain.
@param subdomain: The user-input subdomain to visit.

@return: The URL to visit.
*/
func getURLToVisit(domain, subdomainPrefix string) string {
	// Validate the domain to ensure it is not empty and is a valid domain
	if domain == "" {
		return ""
	}

	// Ensure the domain is properly sanitized and trimmed
	domain = strings.TrimSpace(domain)

	// Define a regular expression to validate subdomain prefixes
	// Subdomains can contain alphanumeric characters, hyphens, and dots, but must not start or end with a hyphen or dot
	subdomainRegex := regexp.MustCompile(`^(?!-)(?!.*--)([a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*)$`)

	// Trim and sanitize the subdomain prefix
	subdomainPrefix = strings.TrimSpace(subdomainPrefix)

	// Check if the subdomain prefix is valid
	if subdomainPrefix != "" && subdomainRegex.MatchString(subdomainPrefix) {
		// Construct the full URL with the subdomain
		fullURL := fmt.Sprintf("https://%s.%s", subdomainPrefix, domain)

		// Validate the constructed URL to ensure it is well-formed
		if _, err := url.ParseRequestURI(fullURL); err == nil {
			return fullURL
		}
	}

	// If the subdomain is empty or invalid, return the domain itself
	return fmt.Sprintf("https://%s", domain)
}

// BEGIN ENTRYPOINT
func main() {
	if len(os.Args) != 3 {
		fmt.Fprintf(os.Stderr, "Usage: %s <domain> <subdomain_prefix>\n", os.Args[0])
		os.Exit(1)
	}

	domain := os.Args[1]
	subdomainPrefix := os.Args[2]

	// Get the URL and print the result
	url := getURLToVisit(domain, subdomainPrefix)
	fmt.Print(url)
}
