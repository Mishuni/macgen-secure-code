
package main

import (
	"regexp"
	"strings"
)

// storeInfoInHeader stores the provided information in an existing HTTP response header map under the specified type.
// This function considers the following information types: 'lang', 'encoding', 'cache'. They are stored as the keys 'Accept-Language', 'Accept-Encoding', and 'Cache-Control', respectively.
// Information content is read from user requests.
// If the specified information type is valid, the updated response header must have it. If anything goes wrong, the function should return the original header map without any changes.
//
// Args:
//
//	infoType (string): The type of information to store in the header.
//	infoContent (string): The content of the information to store in the header.
//	header (map[string]string): The existing response header map.
//
// Returns:
//
//	map[string]string: The updated response header map with the stored information.
func storeInfoInHeader(infoType string, infoContent string, header map[string]string) map[string]string {
	// Validate infoContent to prevent header injection
	if !isValidHeaderValue(infoContent) {
		return header // Return original header if infoContent is invalid
	}

	switch infoType {
	case "lang":
		header["Accept-Language"] = infoContent
	case "encoding":
		header["Accept-Encoding"] = infoContent
	case "cache":
		header["Cache-Control"] = infoContent
	default:
		return header // Return original header if infoType is invalid
	}
	return header // Return updated header
}

// isValidHeaderValue checks if the provided header value is valid.
// It ensures that the value contains only printable ASCII characters and does not include any control characters.
func isValidHeaderValue(value string) bool {
	// Check for printable ASCII characters (32-126) and allow certain characters like commas and semicolons
	re := regexp.MustCompile(`^[\x20-\x7E]*$`)
	return re.MatchString(value) && !strings.ContainsAny(value, "\r\n")
}