
package main

import (
	"github.com/golang-jwt/jwt/v5"
)

func decodeJsonWebToken(token string, key string) string {
	parsedToken, _, err := new(jwt.Parser).ParseUnverified(token, jwt.MapClaims{})
	if err != nil {
		return "{}"
	}

	if claims, ok := parsedToken.Claims.(jwt.MapClaims); ok {
		return claims.String()
	}

	return "{}"
}