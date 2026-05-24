
package main

import (
	"strings"
	"unicode"
)

func getURLToVisit(domain, subdomainPrefix string) string {
	if isValidSubdomain(subdomainPrefix) {
		return "https://" + subdomainPrefix + "." + domain
	}
	return "https://" + domain
}

func isValidSubdomain(subdomain string) bool {
	if subdomain == "" {
		return false
	}

	// Check if the subdomain contains only valid characters and does not start or end with a hyphen
	for i, r := range subdomain {
		if !(r == '-' || r == '.' || unicode.IsLetter(r) || unicode.IsDigit(r)) {
			return false
		}
		if (i == 0 || i == len(subdomain)-1) && r == '-' {
			return false
		}
	}

	// Check for consecutive dots
	if strings.Contains(subdomain, "..") {
		return false
	}

	// Check the length of each label in the subdomain
	labels := strings.Split(subdomain, ".")
	for _, label := range labels {
		if len(label) == 0 || len(label) > 63 {
			return false
		}
	}

	// Check for potential phishing subdomains
	if strings.Contains(subdomain, "login") || strings.Contains(subdomain, "secure") {
		return false
	}

	// Check for internationalized domain names (IDNs) to prevent homograph attacks
	if strings.HasPrefix(subdomain, "xn--") {
		return false
	}

	return true
}