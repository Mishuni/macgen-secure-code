package main

import (
	"fmt"
	"net/url"
	"os"
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
	// Check if the subdomain contains only valid characters
	for _, r := range subdomain {
		if !(r == '-' || r == '.' || (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9')) {
			return false
		}
	}
	// Check if the subdomain is a valid URL
	_, err := url.ParseRequestURI("https://" + subdomain + ".example.com")
	return err == nil
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
