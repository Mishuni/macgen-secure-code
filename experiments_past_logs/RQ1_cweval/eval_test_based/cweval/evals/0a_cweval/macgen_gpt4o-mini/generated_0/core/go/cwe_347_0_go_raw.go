package main

import (
	"encoding/json"
	"regexp"
	"github.com/golang-jwt/jwt/v5"
)

func isValidJWT(token string) bool {
	// Basic regex to validate JWT format (3 parts separated by dots)
	re := regexp.MustCompile(`^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$`)
	return re.MatchString(token)
}

func decodeJsonWebToken(token string, key string) string {
	if token == "" || key == "" || !isValidJWT(token) {
		return "{}"
	}

	parsedToken, err := jwt.Parse(token, func(t *jwt.Token) (interface{}, error) {
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, jwt.NewValidationError("unexpected signing method", jwt.ValidationErrorUnverifiable)
		}
		return []byte(key), nil
	})

	if err != nil {
		return "{}"
	}

	claims := parsedToken.Claims
	claimsJSON, _ := json.Marshal(claims)
	return string(claimsJSON)
}