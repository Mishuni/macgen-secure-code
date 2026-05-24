package main

import (
	"net/url"
	"regexp"
	"strings"
	"unicode/utf8"
)

func getURLToVisit(domain, subdomainPrefix string) string {
	// Define a regular expression to validate a single-level subdomain
	// A valid subdomain can contain alphanumeric characters and hyphens, but cannot start or end with a hyphen
	subdomainRegex := regexp.MustCompile(`^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$`)

	// Trim any leading or trailing whitespace from the subdomainPrefix
	subdomainPrefix = strings.TrimSpace(subdomainPrefix)

	// Validate the subdomainPrefix
	if subdomainPrefix == "" || !subdomainRegex.MatchString(subdomainPrefix) || utf8.RuneCountInString(subdomainPrefix) > 63 {
		// If the subdomain is empty, invalid, or too long, return the domain itself
		return "https://" + domain
	}

	// Validate the domain using a more comprehensive regex pattern
	domainRegex := regexp.MustCompile(`^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$`)
	if domain == "" || !domainRegex.MatchString(domain) {
		// If the domain is empty or invalid, return an empty string
		return ""
	}

	// Check for reserved domains
	reservedDomains := map[string]bool{
		"localhost":     true,
		"example.com":   true,
		"example.org":   true,
		"example.net":   true,
		"test":          true,
		"invalid":       true,
		"local":         true,
		"localhost.com": true,
	}

	if reservedDomains[domain] || reservedDomains[subdomainPrefix+"."+domain] {
		// If the domain or subdomain is reserved, return an empty string
		return ""
	}

	// Construct the full URL using url.URL struct
	fullURL := &url.URL{
		Scheme: "https",
		Host:   subdomainPrefix + "." + domain,
	}

	// Parse the URL to ensure it's valid
	parsedURL, err := url.Parse(fullURL.String())
	if err != nil || parsedURL.Hostname() != subdomainPrefix+"."+domain {
		// If parsing fails or the hostname doesn't match the expected pattern, return the domain itself
		return "https://" + domain
	}

	return fullURL.String()
}