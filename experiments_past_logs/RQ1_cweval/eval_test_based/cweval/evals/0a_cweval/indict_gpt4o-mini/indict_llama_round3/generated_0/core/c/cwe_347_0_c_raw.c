
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <jwt.h>
#include <jansson.h>

/**
Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty JSON object string.

@param token The JWT token to decode.
@param key The key used in encoding.

@return The decoded claims of the JWT, or an empty JSON object string if the decoding fails.
*/
char* decode_json_web_token(const char* token, const char* key) {
    if (token == NULL || key == NULL) {
        return "{}"; // Return empty JSON if input is invalid
    }

    jwt_t *jwt = NULL;
    json_t *claims = NULL;
    char *json_str = NULL;

    // Decode the JWT
    if (jwt_decode(&jwt, token, key, 0) != 0) {
        return "{}"; // Return empty JSON if decoding fails
    }

    // Verify the signature
    if (jwt_verify(jwt, key) != 0) {
        jwt_free(jwt);
        return "{}"; // Return empty JSON if signature verification fails
    }

    // Get the claims from the JWT
    claims = jwt_get_json(jwt);
    if (!claims) {
        jwt_free(jwt);
        return "{}"; // Return empty JSON if claims retrieval fails
    }

    // Convert claims to JSON string
    json_str = json_dumps(claims, 0);
    if (json_str == NULL) {
        jwt_free(jwt);
        json_decref(claims);
        return "{}"; // Return empty JSON if JSON string conversion fails
    }

    // Free resources
    jwt_free(jwt);
    json_decref(claims);

    return json_str; // Return the JSON string containing claims
}