package main

import (
	"fmt"
	"net/http"
	"net/url"
	"regexp"
	"strings"
	"time"
)

// getURLToVisit constructs a secure URL based on the provided domain and subdomain prefix.
func getURLToVisit(domain, subdomainPrefix string) (string, error) {
	// Define a regex pattern for valid subdomain characters
	validSubdomainPattern := `^(?!-)[a-zA-Z0-9-]{1,63}(?<!-)(\.[a-zA-Z0-9-]{1,63})*$`
	isValidSubdomain := regexp.MustCompile(validSubdomainPattern)

	// Trim whitespace and check if the subdomain is valid
	subdomainPrefix = strings.TrimSpace(subdomainPrefix)
	if subdomainPrefix != "" && !isValidSubdomain.MatchString(subdomainPrefix) {
		return "", fmt.Errorf("invalid subdomain prefix: %s", subdomainPrefix)
	}

	// Validate the domain
	if !isValidDomain(domain) {
		return "", fmt.Errorf("invalid domain: %s", domain)
	}

	// Construct the URL
	urlToVisit := "https://" + domain
	if subdomainPrefix != "" {
		urlToVisit = "https://" + subdomainPrefix + "." + domain
	}

	// Check if the domain supports HTTPS
	if !isHTTPSupported(urlToVisit) {
		return "", fmt.Errorf("HTTPS not supported for the domain: %s", urlToVisit)
	}

	return urlToVisit, nil
}

// isValidDomain checks if the domain is well-formed and trusted.
func isValidDomain(domain string) bool {
	// Implement domain validation logic (e.g., check for valid format)
	domainPattern := `^(?!-)[a-zA-Z0-9-]{1,63}(?<!-)(\.[a-zA-Z0-9-]{1,63})+$`
	isValidDomain := regexp.MustCompile(domainPattern)
	return isValidDomain.MatchString(domain)
}

// isHTTPSupported checks if the given URL supports HTTPS.
func isHTTPSupported(urlToVisit string) bool {
	client := http.Client{
		Timeout: 5 * time.Second, // Set a timeout for the request
	}
	resp, err := client.Head(urlToVisit)
	if err != nil {
		return false
	}
	defer resp.Body.Close() // Ensure the response body is closed
	return resp.StatusCode == http.StatusOK
}