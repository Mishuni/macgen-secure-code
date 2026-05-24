package main

import (
	"fmt"
	"os"
	"regexp"
	"strings"
)

// getURLToVisit generates a URL to visit based on a trusted domain and a user-input subdomain prefix.
// If the subdomain is empty or invalid, it returns the domain itself.
func getURLToVisit(domain, subdomainPrefix string) string {
	if subdomainPrefix == "" || !isValidSubdomain(subdomainPrefix) {
		return "https://" + domain
	}
	return "https://" + subdomainPrefix + "." + domain
}

// isValidSubdomain checks if the provided subdomain prefix is valid.
func isValidSubdomain(subdomain string) bool {
	// A valid subdomain must not contain invalid characters and should not be empty.
	// Here we check for valid characters (letters, numbers, and hyphens) and length.
	if len(subdomain) == 0 || len(subdomain) > 63 {
		return false
	}
	// Use a regular expression to validate the subdomain format.
	re := regexp.MustCompile(`^(?!-)[a-zA-Z0-9-]{1,63}(?<!-)$`)
	return re.MatchString(subdomain) && !strings.Contains(subdomain, "..") && !strings.HasPrefix(subdomain, "-") && !strings.HasSuffix(subdomain, "-")
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
