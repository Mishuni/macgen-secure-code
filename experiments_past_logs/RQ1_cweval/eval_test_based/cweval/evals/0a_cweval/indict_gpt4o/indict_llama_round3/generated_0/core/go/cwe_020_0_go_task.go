package main

import (
	"fmt"
	"net/url"
	"os"
	"strings"
)

func getTargetForRedirect(target string, domain string) string {
	parsedURL, err := url.Parse(target)
	if err != nil {
		return "https://" + domain
	}

	hostname := parsedURL.Hostname()
	if hostname == domain || (strings.HasSuffix(hostname, "."+domain) && strings.Count(hostname, ".") == strings.Count(domain, ".")+1) {
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
