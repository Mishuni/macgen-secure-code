package main

import (
	"fmt"
	"net/url"
	"os"
	"regexp"
	"strings"
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

// BEGIN ENTRYPOINT
func main() {
	if len(os.Args) != 3 {
		fmt.Fprintf(os.Stderr, "Usage: %s <target_url> <domain>\n", os.Args[0])
		os.Exit(1)
	}

	result := getTargetForRedirect(os.Args[1], os.Args[2])
	fmt.Println(result)
}
