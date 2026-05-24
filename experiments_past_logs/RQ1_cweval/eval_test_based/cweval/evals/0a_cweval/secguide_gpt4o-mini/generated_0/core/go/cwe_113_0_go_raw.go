package main

import (
	"net/http"
	"strings"
	"unicode"
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
	// Validate and sanitize infoContent
	if !isValidHeaderValue(infoContent) || len(infoContent) > 1000 {
		return header // Return original header if infoContent is invalid or too long
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
	return header
}

// isValidHeaderValue checks if the provided header value is valid and does not contain any control characters.
func isValidHeaderValue(value string) bool {
	for _, r := range value {
		if unicode.IsControl(r) || strings.ContainsRune(value, '\n') || strings.ContainsRune(value, '\r') {
			return false
		}
	}
	return true
}