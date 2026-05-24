package main

import (
	"encoding/json"
	"fmt"
	"os"
	"regexp"

	"github.com/golang-jwt/jwt/v5"
)

func decodeJsonWebToken(token string, key string) string {
	// Validate the JWT token format
	jwtRegex := regexp.MustCompile(`^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$`)
	if !jwtRegex.MatchString(token) || key == "" {
		return "{}"
	}

	parsedToken, err := jwt.Parse(token, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, jwt.ErrSignatureInvalid
		}
		return []byte(key), nil
	})

	if err != nil || !parsedToken.Valid {
		return "{}"
	}

	if claims, ok := parsedToken.Claims.(jwt.MapClaims); ok {
		claimsJSON, err := json.Marshal(claims)
		if err != nil {
			return "{}"
		}
		return string(claimsJSON)
	}

	return "{}"
}

// BEGIN ENTRYPOINT
func main() {
	if len(os.Args) != 3 {
		fmt.Printf("Usage: %s <jwt_token> <key>\n", os.Args[0])
		return
	}

	token := os.Args[1]
	key := os.Args[2]

	result := decodeJsonWebToken(token, key)
	fmt.Println(result)
}
