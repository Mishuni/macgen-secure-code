package main

import (
	"fmt"
	"net/url"
	"os"
	"strings"
)

var allowedDomains = []string{
	"example.com",
	"music.example.com",
	"blog.example.com",
	// Add more allowed domains as needed
}

func sanitizeDomain(domain string) string {
	return strings.TrimSpace(domain)
}

func isAllowedDomain(target string) bool {
	parsedTarget, err := url.Parse(target)
	if err != nil {
		return false
	}
	for _, allowed := range allowedDomains {
		if parsedTarget.Hostname() == allowed {
			return true
		}
	}
	return false
}

func isValidRedirect(target string, domain string) bool {
	parsedTarget, err := url.Parse(target)
	if err != nil {
		return false
	}
	return parsedTarget.Scheme == "https" && strings.HasSuffix(parsedTarget.Hostname(), domain)
}

func getTargetForRedirect(target string, domain string) string {
	domain = sanitizeDomain(domain)

	if isAllowedDomain(target) && isValidRedirect(target, domain) {
		return target
	}
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
