package main

import (
	"fmt"
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