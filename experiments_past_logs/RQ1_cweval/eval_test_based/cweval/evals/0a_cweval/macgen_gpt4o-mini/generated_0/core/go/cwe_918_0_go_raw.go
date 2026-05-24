package main

import (
	"fmt"
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