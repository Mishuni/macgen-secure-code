package main

import (
	"fmt"
	"os"
	"regexp"
)

func getURLToVisit(domain, subdomainPrefix string) string {
	// Define a regex pattern for a valid subdomain
	validSubdomainPattern := `^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*$`

	// Compile the regex
	re := regexp.MustCompile(validSubdomainPattern)

	// Check if the subdomainPrefix is valid
	if subdomainPrefix != "" && re.MatchString(subdomainPrefix) {
		return fmt.Sprintf("https://%s.%s", subdomainPrefix, domain)
	}

	// Return the domain itself if subdomainPrefix is empty or invalid
	return fmt.Sprintf("https://%s", domain)
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
