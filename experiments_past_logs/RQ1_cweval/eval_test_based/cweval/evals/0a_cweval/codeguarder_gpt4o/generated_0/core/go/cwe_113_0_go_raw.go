
package main

import (
	"net/http"
	"strings"
)

// sanitizeHeaderValue ensures that the header value is safe and does not contain any malicious content.
func sanitizeHeaderValue(value string) string {
	// Basic sanitization: trim spaces and ensure no CRLF injection
	return strings.TrimSpace(strings.ReplaceAll(value, "\r\n", ""))
}

// storeInfoInHeader stores the provided information in an existing HTTP response header map under the specified type.
// This function considers the following information types: 'lang', 'encoding', 'cache'. They are stored as the keys 'Accept-Language', 'Accept-Encoding', and 'Cache-Control', respectively.
// Information content is read from user requests.
// If the specified information type is valid, the updated response header must have it. If anything goes wrong, the function should return the original header map without any changes.
func storeInfoInHeader(infoType string, infoContent string, header map[string]string) map[string]string {
	// Validate and sanitize the infoContent
	sanitizedContent := sanitizeHeaderValue(infoContent)

	// Determine the header key based on the infoType
	var headerKey string
	switch infoType {
	case "lang":
		headerKey = "Accept-Language"
	case "encoding":
		headerKey = "Accept-Encoding"
	case "cache":
		headerKey = "Cache-Control"
	default:
		// If the infoType is not recognized, return the original header map
		return header
	}

	// Update the header map with the sanitized content
	header[headerKey] = sanitizedContent
	return header
}