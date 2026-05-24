package main

import (
	"encoding/json"
	"errors"
	"github.com/golang-jwt/jwt/v5"
	"os"
	"time"
)

// Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty JSON object string.
// @param token The JWT token to decode.
// @param key The key used in encoding.
// @return The decoded claims of the JWT, or an empty JSON object string if the decoding fails.
func decodeJsonWebToken(token string, key string) string {
	claims := struct {
		Exp int64 `json:"exp"`
		Iss string `json:"iss,omitempty"`
		Aud string `json:"aud,omitempty"`
	}{}

	tkn, err := jwt.ParseWithClaims(token, &claims, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, jwt.NewValidationError("unexpected signing method", jwt.ValidationErrorUnverifiable)
		}
		return []byte(key), nil
	})

	if err != nil || !tkn.Valid {
		return "{}"
	}

	if claims.Exp != 0 && time.Now().Unix() > claims.Exp {
		return "{}" // Token is expired
	}

	claimsJSON, err := json.Marshal(claims)
	if err != nil {
		return "{}" // Handle marshaling error
	}

	return string(claimsJSON)
}