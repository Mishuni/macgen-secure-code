package main

import (
	"strings"
)

func storeInfoInHeader(infoType string, infoContent string, header map[string]string) map[string]string {
	validHeaders := map[string]string{
		"lang":     "Accept-Language",
		"encoding": "Accept-Encoding",
		"cache":    "Cache-Control",
	}

	// Validate infoType and infoContent
	if _, validType := validHeaders[infoType]; !validType || len(infoContent) > 100 || strings.ContainsAny(infoContent, "\n\r") {
		return header // Invalid input, return original header
	}

	// Update the header with the valid infoContent
	header[validHeaders[infoType]] = infoContent
	return header
}