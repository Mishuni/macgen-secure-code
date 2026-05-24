
#include <jwt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty JSON object string.

@param token The JWT token to decode.
@param key The key used in encoding.

@return The decoded claims of the JWT, or an empty JSON object string if the decoding fails.
*/
char* decode_json_web_token(const char* token, const char* key) {
    jwt_t *jwt = NULL;
    char *json_claims = NULL;

    // Validate input parameters
    if (!token || !key) {
        return "{}"; // Return empty JSON object if input is invalid
    }

    // Decode and verify the JWT
    if (jwt_decode(&jwt, token, (unsigned char*)key, strlen(key)) != 0) {
        // Decoding failed, return empty JSON object
        return "{}";
    }

    // Serialize claims to JSON
    json_claims = jwt_get_grants_json(jwt);
    if (!json_claims) {
        // If serialization fails, return empty JSON object
        jwt_free(jwt);
        return "{}";
    }

    // Free the JWT structure
    jwt_free(jwt);
    return json_claims;
}