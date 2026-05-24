
package main

import (
	"encoding/json"
	"github.com/golang-jwt/jwt/v5"
	"strings"
)

// decodeJsonWebToken decodes the JSON Web Token (JWT) and returns its claims. 
// The token is encoded with the HS256 algorithm. If the decoding fails, 
// it returns an empty JSON object string.
// 
// @param token The JWT token to decode.
// @param key The key used in encoding.
// 
// @return The decoded claims of the JWT, or an empty JSON object string if the decoding fails.
func decodeJsonWebToken(token string, key string) string {
	// Validate the token format
	parts := strings.Split(token, ".")
	if len(parts) != 3 {
		return "{}"
	}

	claims := jwt.MapClaims{}
	tkn, err := jwt.ParseWithClaims(token, &claims, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, jwt.NewValidationError("unexpected signing method", jwt.ValidationErrorUnverifiable)
		}
		return []byte(key), nil
	})

	if err != nil || !tkn.Valid {
		return "{}"
	}

	// Marshal claims to JSON
	claimsJSON, err := json.Marshal(claims)
	if err != nil {
		return "{}"
	}
	return string(claimsJSON)
}