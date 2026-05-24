package main

import (
	"net/url"
	"strings"
	"regexp"
)

func getTargetForRedirect(target string, domain string) string {
	if !isValidDomain(domain) {
		return "https://" + domain
	}

	parsedURL, err := url.Parse(target)
	if err != nil {
		return "https://" + domain
	}

	host := parsedURL.Hostname()
	if strings.HasSuffix(host, "."+domain) || host == domain {
		return target
	}

	return "https://" + domain
}

func isValidDomain(domain string) bool {
	// Simple regex to validate domain names
	re := regexp.MustCompile(`^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$`)
	return re.MatchString(domain)
}