package main

import (
	"strings"
)

func storeInfoInHeader(infoType string, infoContent string, header map[string]string) map[string]string {
	if !isValidInfoType(infoType) {
		return header
	}

	infoContent = sanitizeContent(infoContent)

	switch infoType {
	case "lang":
		header["Accept-Language"] = infoContent
	case "encoding":
		header["Accept-Encoding"] = infoContent
	case "cache":
		header["Cache-Control"] = infoContent
	}
	return header
}

func isValidInfoType(infoType string) bool {
	return infoType == "lang" || infoType == "encoding" || infoType == "cache"
}

func sanitizeContent(content string) string {
	// Basic sanitization: trim spaces and escape newlines
	content = strings.TrimSpace(content)
	content = strings.ReplaceAll(content, "\n", "")
	content = strings.ReplaceAll(content, "\r", "")
	return content
}