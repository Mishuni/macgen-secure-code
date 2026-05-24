package main

import (
	"fmt"
	"os"
	"regexp"
)

var (
	subdomainRegex = regexp.MustCompile(`^([a-zA-Z0-9-]{1,63}\.)*[a-zA-Z0-9-]{1,63}$`)
	domainRegex    = regexp.MustCompile(`^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$`)
)

func getURLToVisit(domain, subdomainPrefix string) string {
	if !isValidDomain(domain) {
		return domain
	}
	if !isValidSubdomain(subdomainPrefix) {
		return "https://" + domain
	}
	return fmt.Sprintf("https://%s.%s", subdomainPrefix, domain)
}

func isValidSubdomain(subdomain string) bool {
	return subdomainRegex.MatchString(subdomain)
}

func isValidDomain(domain string) bool {
	return domainRegex.MatchString(domain)
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
